from typing import Optional

from sqlalchemy.orm import Session, exc

from platypush.entities import Entity


def get_parent(session: Session, entity: Entity) -> Optional[Entity]:
    """
    Gets the parent of an entity, and it fetches if it's not available in
    the current session.
    """
    try:
        return entity.parent
    except exc.DetachedInstanceError:
        # Dirty fix for `Parent instance <...> is not bound to a Session;
        # lazy load operation of attribute 'parent' cannot proceed`
        return session.query(Entity).get(entity.parent_id) if entity.parent_id else None
