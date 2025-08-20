from abc import ABC, abstractmethod
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Collection, Dict, Generator, List, Optional, Type, Union

from sqlalchemy import and_, exists, or_, func, literal, case
from sqlalchemy.orm import Session

from platypush.common.notes import Note, NoteCollection

from .._model import ApiSettings, Item, ItemType, Results
from ..db._model import (
    Note as DbNote,
    NoteCollection as DbNoteCollection,
    NoteContentIndex as DbNoteContentIndex,
)
from .search import SearchMixin


class NotesIndexMixin(SearchMixin, ABC):  # pylint: disable=too-few-public-methods
    """
    Mixin that provides methods for managing and searching the notes index in
    the database.
    """

    _api_settings: ApiSettings
    _plugin_name: str

    @abstractmethod
    @contextmanager
    def _get_db_session(self, *args, **kwargs) -> Generator[Session, None, None]:
        """
        Context manager to get a database session.
        """

    @abstractmethod
    def _from_db_note(self, db_note: DbNote) -> Note:
        ...

    @abstractmethod
    def _from_db_collection(self, db_collection: DbNoteCollection) -> NoteCollection:
        ...

    def _refresh_content_index(self, notes: Collection[Note], session: Session) -> None:
        """
        Refresh the content index for the given notes.
        """
        # Don't refresh the content index if the backend API already supports search
        if self._api_settings.supports_search:
            return

        for note in notes:
            if not note.content:
                continue

            tokens = [
                DbNoteContentIndex(
                    note_id=note._db_id,  # pylint:disable=protected-access
                    token=token.token,
                    length=token.length,
                    count=token.count,
                )
                for token in self.tokenize(note.content)
            ]

            session.query(DbNoteContentIndex).filter(
                DbNoteContentIndex.note_id
                == note._db_id  # pylint:disable=protected-access
            ).delete()

            session.add_all(tokens)

    @staticmethod
    def _search_content_exact_score(session: Session, note_id: Any, term: str):
        """
        Subquery to calculate the score for exact token matches in note content.
        """
        # Sum 0.5 * length * count for exact token match
        return (
            session.query(
                func.coalesce(
                    func.sum(
                        0.5 * DbNoteContentIndex.length * DbNoteContentIndex.count
                    ),
                    0,
                )
            )
            .filter(DbNoteContentIndex.note_id == note_id)
            .filter(DbNoteContentIndex.token == term)
            .correlate(DbNote)
            .as_scalar()
        )

    @staticmethod
    def _search_content_wildcard_score(session: Session, note_id: Any, term: str):
        """
        Subquery to calculate the score for wildcard token matches in note content.
        """
        # Sum 0.1 * length * count for wildcard token match (excluding exact matches)
        return (
            session.query(
                func.coalesce(
                    func.sum(
                        0.1 * DbNoteContentIndex.length * DbNoteContentIndex.count
                    ),
                    0,
                )
            )
            .filter(DbNoteContentIndex.note_id == note_id)
            .filter(DbNoteContentIndex.token.like(f'%{term}%'))
            .filter(DbNoteContentIndex.token != term)
            .correlate(DbNote)
            .as_scalar()
        )

    @staticmethod
    def _search_get_query_match_filter(
        session: Session,
        terms: Collection[str],
        db_model: Union[Type[DbNote], Type[DbNoteCollection]],
    ) -> List:
        """
        Get a list of SQLAlchemy filters for exact match search terms.
        """
        filters = []
        for term in terms:
            term_filters = [
                # TODO Create indexes on title and description
                func.lower(db_model.title).like(f'%{term}%'),
                func.lower(db_model.description).like(f'%{term}%'),
                *(
                    [
                        session.query(DbNoteContentIndex)
                        .filter(DbNoteContentIndex.note_id == DbNote.id)
                        .filter(DbNoteContentIndex.token == term)
                        .exists()
                    ]
                    if issubclass(db_model, DbNote)
                    else []
                ),
            ]
            filters.append(or_(*term_filters))

        return filters

    @staticmethod
    def _search_get_query_wildcard_filter(
        session: Session,
        terms: Collection[str],
        db_model: Union[Type[DbNote], Type[DbNoteCollection]],
    ) -> List:
        """
        Get a list of SQLAlchemy filters for wildcard search terms.
        """
        filters = []
        for term in terms:
            like_pattern = term.replace('*', '%')
            term_filters = [
                func.lower(db_model.title).like(like_pattern),
                func.lower(db_model.description).like(like_pattern),
                *(
                    [
                        session.query(DbNoteContentIndex)
                        .filter(DbNoteContentIndex.note_id == DbNote.id)
                        .filter(DbNoteContentIndex.token.like(like_pattern))
                        .exists()
                    ]
                    if issubclass(db_model, DbNote)
                    else []
                ),
            ]
            filters.append(or_(*term_filters))

        return filters

    def _search_get_parent_filter(
        self,
        db_model: Union[Type["DbNote"], Type["DbNoteCollection"]],
        parent_id: str,
        include: bool = True,
    ):
        """
        Returns an EXISTS or NOT EXISTS filter for parent based on external_id and plugin.
        """
        # We want db_model.parent_id to point to a collection whose external_id matches parent.external_id
        parent_exists = exists().where(
            and_(
                db_model.parent_id == DbNoteCollection.id,
                DbNoteCollection.external_id == parent_id,
                DbNoteCollection.plugin == self._plugin_name,
            )
        )

        return parent_exists if include else ~parent_exists

    def _search_get_include_exclude_filters(
        self,
        db_model: Union[Type[DbNote], Type[DbNoteCollection]],
        include_terms: Optional[Dict[str, Any]] = None,
        exclude_terms: Optional[Dict[str, Any]] = None,
    ) -> List:
        """
        Get a list of SQLAlchemy filters for include and exclude terms.
        """
        filters = []
        include_terms = dict(include_terms or {})
        exclude_terms = dict(exclude_terms or {})

        # Handle 'parent' transparently. If it exists in include_terms, We
        # want to include only items whose parent matches the given (external)
        # ID and plugin.
        parent_id = include_terms.pop("parent", None)
        if parent_id is not None:
            filters.append(
                self._search_get_parent_filter(
                    db_model=db_model, parent_id=parent_id, include=True
                )
            )

        # Handle 'parent' transparently in exclude_terms as well.
        parent_id = exclude_terms.pop("parent", None)
        if parent_id is not None:
            filters.append(
                self._search_get_parent_filter(
                    db_model=db_model, parent_id=parent_id, include=False
                )
            )

        # Regular include/exclude columns
        for col, val in (include_terms or {}).items():
            column = getattr(db_model, col, None)
            if column is not None:
                filters.append(column == val)

        for col, val in (exclude_terms or {}).items():
            column = getattr(db_model, col, None)
            if column is not None:
                filters.append(column != val)

        return filters

    @staticmethod
    def _search_get_time_filters(
        db_model: Union[Type[DbNote], Type[DbNoteCollection]],
        created_before: Optional[datetime] = None,
        created_after: Optional[datetime] = None,
        updated_before: Optional[datetime] = None,
        updated_after: Optional[datetime] = None,
    ) -> List:
        """
        Get a list of SQLAlchemy filters for time-based queries.
        """
        filters = []
        if created_before:
            filters.append(db_model.created_at < created_before)
        if created_after:
            filters.append(db_model.created_at > created_after)
        if updated_before:
            filters.append(db_model.updated_at < updated_before)
        if updated_after:
            filters.append(db_model.updated_at > updated_after)

        return filters

    def _search_get_total_score(
        self,
        session: Session,
        db_model: Union[Type[DbNote], Type[DbNoteCollection]],
        search_terms: Collection[str],
    ) -> Any:
        total_score = literal(0)
        for term in search_terms:
            # Boost scores for title by 20
            total_score += case(
                (func.lower(db_model.title).like(f'%{term}%'), 20), else_=0
            )
            # Boost scores for description by 5
            total_score += case(
                (func.lower(db_model.description).like(f'%{term}%'), 5), else_=0
            )

            if issubclass(db_model, DbNote):
                total_score += self._search_content_exact_score(
                    session, DbNote.id, term
                )
                total_score += self._search_content_wildcard_score(
                    session, DbNote.id, term
                )

        return total_score.label('total_score')

    def _db_search(
        self,
        query: str,
        *_,
        item_type: ItemType,
        include_terms: Optional[Dict[str, Any]] = None,
        exclude_terms: Optional[Dict[str, Any]] = None,
        created_before: Optional[datetime] = None,
        created_after: Optional[datetime] = None,
        updated_before: Optional[datetime] = None,
        updated_after: Optional[datetime] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = 0,
        **__,
    ) -> Results:
        """
        Search for notes or collections using the internal index.

        This should only be used by plugins that don't provide their own search
        API (like Nextcloud Notes or any local notes plugin).
        """
        query = query.lower().strip()
        search_terms = self.extract_search_terms(query)
        wildcard_terms = {term for term in search_terms if '*' in term}
        match_terms = {term for term in search_terms if term not in wildcard_terms}

        with self._get_db_session() as session:
            if item_type == ItemType.NOTE:
                db_model = DbNote
            elif item_type == ItemType.COLLECTION:
                db_model = DbNoteCollection
            else:
                raise ValueError(f'Unsupported item type: {item_type}')

            filters = [
                db_model.plugin == self._plugin_name,
                *self._search_get_include_exclude_filters(
                    db_model=db_model,
                    include_terms=include_terms,
                    exclude_terms=exclude_terms,
                ),
                *self._search_get_time_filters(
                    db_model=db_model,
                    created_before=created_before,
                    created_after=created_after,
                    updated_before=updated_before,
                    updated_after=updated_after,
                ),
                *self._search_get_query_match_filter(
                    session=session, terms=match_terms, db_model=db_model
                ),
                *self._search_get_query_wildcard_filter(
                    session=session, terms=wildcard_terms, db_model=db_model
                ),
            ]

            total_score = self._search_get_total_score(
                session=session,
                db_model=db_model,
                search_terms=search_terms,
            )

            query_obj = (
                session.query(db_model, total_score.label("boost_score"))
                .filter(and_(*filters))
                .order_by(total_score.desc())
                .distinct()
            )

            if limit is not None:
                query_obj = query_obj.offset(offset).limit(limit)
            if offset is not None:
                query_obj = query_obj.offset(offset)

            return Results(
                items=[
                    Item(
                        item=(
                            self._from_db_note(item[0])
                            if item_type == ItemType.NOTE
                            else self._from_db_collection(item[0])
                        ),
                        type=item_type,
                    )
                    for item in query_obj.all()
                ],
            )
