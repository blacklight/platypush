import todoist.models

import datetime

from typing import Optional, List, Dict, Any

from platypush.message import Mapping
from platypush.message.response import Response


class TodoistResponse(Response):
    pass


class TodoistUserResponse(TodoistResponse):
    def __init__(self,
                 auto_reminder: Optional[int] = None,
                 avatar_big: Optional[str] = None,
                 avatar_medium: Optional[str] = None,
                 avatar_s640: Optional[str] = None,
                 avatar_small: Optional[str] = None,
                 business_account_id: Optional[int] = None,
                 daily_goal: Optional[int] = None,
                 date_format: Optional[str] = None,
                 dateist_inline_disabled: Optional[bool] = None,
                 dateist_lang: Optional[str] = None,
                 days_off: Optional[List[int]] = None,
                 default_reminder: Optional[str] = None,
                 email: Optional[str] = None,
                 features: Optional[Dict[str, Any]] = None,
                 full_name: Optional[str] = None,
                 id: Optional[int] = None,
                 image_id: Optional[str] = None,
                 inbox_project: Optional[int] = None,
                 is_biz_admin: Optional[bool] = None,
                 is_premium: Optional[bool] = None,
                 join_date: Optional[datetime.datetime] = None,
                 karma: Optional[float] = None,
                 karma_trend: Optional[str] = None,
                 lang: Optional[str] = None,
                 legacy_inbox_project: Optional[int] = None,
                 mobile_host: Optional[str] = None,
                 mobile_number: Optional[str] = None,
                 next_week: Optional[int] = None,
                 premium_until: Optional[datetime.datetime] = None,
                 share_limit: Optional[int] = None,
                 sort_order: Optional[int] = None,
                 start_day: Optional[int] = None,
                 start_page: Optional[str] = None,
                 theme: Optional[int] = None,
                 time_format: Optional[int] = None,
                 token: Optional[str] = None,
                 tz_info: Optional[Dict[str, Any]] = None,
                 unique_prefix: Optional[int] = None,
                 websocket_url: Optional[str] = None,
                 weekly_goal: Optional[int] = None,
                 **kwargs):
        response = {
            'auto_reminder': auto_reminder,
            'avatar_big': avatar_big,
            'avatar_medium': avatar_medium,
            'avatar_s640': avatar_s640,
            'avatar_small': avatar_small,
            'business_account_id': business_account_id,
            'daily_goal': daily_goal,
            'date_format': date_format,
            'dateist_inline_disabled': dateist_inline_disabled,
            'dateist_lang': dateist_lang,
            'days_off': days_off,
            'default_reminder': default_reminder,
            'email': email,
            'features': features,
            'full_name': full_name,
            'id': id,
            'image_id': image_id,
            'inbox_project': inbox_project,
            'is_biz_admin': is_biz_admin,
            'is_premium': is_premium,
            'join_date': join_date,
            'karma': karma,
            'karma_trend': karma_trend,
            'lang': lang,
            'legacy_inbox_project': legacy_inbox_project,
            'mobile_host': mobile_host,
            'mobile_number': mobile_number,
            'next_week': next_week,
            'premium_until': premium_until,
            'share_limit': share_limit,
            'sort_order': sort_order,
            'start_day': start_day,
            'start_page': start_page,
            'theme': theme,
            'time_format': time_format,
            'token': token,
            'tz_info': tz_info,
            'unique_prefix': unique_prefix,
            'websocket_url': websocket_url,
            'weekly_goal': weekly_goal,
        }

        super().__init__(output=response, **kwargs)


class TodoistProject(Mapping):
    def __init__(self,
                 child_order: int,
                 collapsed: int,
                 color: int,
                 has_more_notes: bool,
                 id: int,
                 is_archived: bool,
                 is_deleted: bool,
                 is_favorite: bool,
                 name: str,
                 shared: bool,
                 inbox_project: Optional[bool] = None,
                 legacy_id: Optional[int] = None,
                 parent_id: Optional[int] = None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.child_order = child_order
        self.collapsed = collapsed
        self.color = color
        self.has_more_notes = has_more_notes
        self.id = id
        self.inbox_project = inbox_project
        self.is_archived = bool(is_archived)
        self.is_deleted = bool(is_deleted)
        self.is_favorite = bool(is_favorite)
        self.name = name
        self.shared = shared
        self.legacy_id = legacy_id
        self.parent_id = parent_id


class TodoistProjectsResponse(TodoistResponse):
    def __init__(self, projects: List[TodoistProject], **kwargs):
        self.projects = [TodoistProject(**(p.data if isinstance(p, todoist.models.Project) else p)) for p in projects]
        super().__init__(output=[p.__dict__ for p in self.projects], **kwargs)


class TodoistItem(Mapping):
    def __init__(self,
                 content: str,
                 id: int,
                 checked: bool,
                 priority: int,
                 child_order: int,
                 collapsed: bool,
                 day_order: int,
                 date_added: datetime.datetime,
                 in_history: bool,
                 is_deleted: bool,
                 user_id: int,
                 has_more_notes: bool = False,
                 project_id: Optional[int] = None,
                 parent_id: Optional[int] = None,
                 responsible_uid: Optional[int] = None,
                 date_completed: Optional[datetime.datetime] = None,
                 assigned_by_uid: Optional[int] = None,
                 due: Optional[Dict[str, Any]] = None,
                 labels: Optional[List[str]] = None,
                 legacy_project_id: Optional[int] = None,
                 section_id: Optional[int] = None,
                 sync_id: Optional[int] = None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.content = content
        self.id = id
        self.checked = bool(checked)
        self.priority = priority
        self.child_order = child_order
        self.collapsed = bool(collapsed)
        self.day_order = day_order
        self.date_added = date_added
        self.has_more_notes = bool(has_more_notes)
        self.in_history = bool(in_history)
        self.is_deleted = bool(is_deleted)
        self.user_id = user_id
        self.project_id = project_id
        self.parent_id = parent_id
        self.responsible_uid = responsible_uid
        self.date_completed = date_completed
        self.assigned_by_uid = assigned_by_uid
        self.due = due
        self.labels = labels
        self.legacy_project_id = legacy_project_id
        self.section_id = section_id
        self.sync_id = sync_id


class TodoistItemsResponse(TodoistResponse):
    def __init__(self, items: List[TodoistItem], **kwargs):
        self.items = [TodoistItem(**(i.data if isinstance(i, todoist.models.Item) else i.__dict__)) for i in items]
        super().__init__(output=[i.__dict__ for i in self.items], **kwargs)


class TodoistFilter(Mapping):
    def __init__(self,
                 color: int,
                 id: int,
                 is_deleted: bool,
                 is_favorite: bool,
                 item_order: int,
                 name: str,
                 query: str,
                 legacy_id: Optional[int] = None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.color = color
        self.id = id
        self.is_deleted = is_deleted
        self.is_favorite = is_favorite
        self.item_order = item_order
        self.name = name
        self.query = query
        self.legacy_id = legacy_id


class TodoistFiltersResponse(TodoistResponse):
    def __init__(self, filters: List[TodoistFilter], **kwargs):
        self.filters = [TodoistFilter(**(f.data if isinstance(f, todoist.models.Filter) else f.__dict__))
                        for f in filters]

        super().__init__(output=[f.__dict__ for f in self.filters], **kwargs)


class TodoistLiveNotification(Mapping):
    def __init__(self,
                 id: int,
                 is_deleted: bool,
                 created: str,
                 is_unread: bool,
                 notification_key: str,
                 notification_type: str,
                 completed_last_month: Optional[int] = None,
                 karma_level: Optional[int] = None,
                 promo_img: Optional[str] = None,
                 completed_tasks: Optional[int] = None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id = id
        self.is_deleted = bool(is_deleted)
        self.completed_last_month = completed_last_month
        self.completed_tasks = completed_tasks
        self.created = created
        self.is_unread = bool(is_unread)
        self.karma_level = karma_level
        self.notification_key = notification_key
        self.notification_type = notification_type
        self.promo_img = promo_img


class TodoistLiveNotificationsResponse(TodoistResponse):
    def __init__(self, notifications: List[TodoistLiveNotification], **kwargs):
        self.notifications = [TodoistLiveNotification(**(n.data if isinstance(n, todoist.models.LiveNotification)
                                                         else n.__dict__)) for n in notifications]

        super().__init__(output=[n.__dict__ for n in self.notifications], **kwargs)


class TodoistCollaborator(Mapping):
    def __init__(self, data: Dict[str, Any], *args, **kwargs):
        super().__init__(*args, **kwargs)
        for k, v in data.items():
            self.__setattr__(k, v)


class TodoistCollaboratorsResponse(TodoistResponse):
    def __init__(self, collaborators: List[TodoistCollaborator], **kwargs):
        self.collaborators = [TodoistCollaborator(c.data if isinstance(c, todoist.models.Collaborator) else c.__dict__)
                              for c in collaborators]

        super().__init__(output=[c.__dict__ for c in self.collaborators], **kwargs)


class TodoistNote(Mapping):
    def __init__(self, data: Dict[str, Any], *args, **kwargs):
        super().__init__(*args, **kwargs)
        for k, v in data.items():
            self.__setattr__(k, v)


class TodoistNotesResponse(TodoistResponse):
    def __init__(self, notes: List[TodoistCollaborator], **kwargs):
        self.notes = [TodoistCollaborator(n.data if isinstance(n, todoist.models.Note) else n.__dict__)
                      for n in notes]

        super().__init__(output=[n.__dict__ for n in self.notes], **kwargs)


class TodoistProjectNote(Mapping):
    def __init__(self, data: Dict[str, Any], *args, **kwargs):
        super().__init__(*args, **kwargs)
        for k, v in data.items():
            self.__setattr__(k, v)


class TodoistProjectNotesResponse(TodoistResponse):
    def __init__(self, notes: List[TodoistCollaborator], **kwargs):
        self.notes = [TodoistCollaborator(n.data if isinstance(n, todoist.models.ProjectNote) else n.__dict__)
                      for n in notes]

        super().__init__(output=[n.__dict__ for n in self.notes], **kwargs)


class TodoistReminder(Mapping):
    def __init__(self, data: Dict[str, Any], *args, **kwargs):
        super().__init__(*args, **kwargs)
        for k, v in data.items():
            self.__setattr__(k, v)


class TodoistRemindersResponse(TodoistResponse):
    def __init__(self, reminders: List[TodoistReminder], **kwargs):
        self.reminders = [TodoistReminder(n.data if isinstance(n, todoist.models.Reminder) else n.__dict__)
                          for n in reminders]

        super().__init__(output=[r.__dict__ for r in self.reminders], **kwargs)


# vim:sw=4:ts=4:et:
