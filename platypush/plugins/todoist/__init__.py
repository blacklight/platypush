import time
from typing import Optional

import todoist
import todoist.managers.items  # type: ignore
import websocket

from platypush.plugins import Plugin, action
from platypush.schemas.todoist import (
    TodoistCollaboratorSchema,
    TodoistFilterSchema,
    TodoistItemSchema,
    TodoistLiveNotificationSchema,
    TodoistNoteSchema,
    TodoistProjectNoteSchema,
    TodoistProjectSchema,
    TodoistUserSchema,
)


class TodoistPlugin(Plugin):
    """
    Todoist integration.

    You'll also need a Todoist token. You can get it `here
    <https://todoist.com/prefs/integrations>`_.
    """

    _sync_timeout = 60.0

    def __init__(self, api_token: str, **kwargs):
        """
        :param api_token: Todoist API token.
            You can get it `here <https://todoist.com/prefs/integrations>`_.
        """

        super().__init__(**kwargs)
        self.api_token = api_token
        self._api = None
        self._last_sync_time = None

        self._ws_url: Optional[str] = None
        self._ws: Optional[websocket.WebSocketApp] = None
        self._connected = False
        self._todoist_initialized = False

        self._items = {}
        self._event_handled = False

    def _get_api(self) -> todoist.TodoistAPI:  # type: ignore
        if not self._api:
            self._api = todoist.TodoistAPI(self.api_token)  # type: ignore

        if (
            not self._last_sync_time
            or time.time() - self._last_sync_time > self._sync_timeout
        ):
            self._api.sync()

        return self._api

    @action
    def get_user(self):
        """
        Get logged user info.

        :return: .. schema:: todoist.TodoistUserSchema
        """
        return TodoistUserSchema().dump(self._get_api().state['user'])

    @action
    def get_projects(self):
        """
        Get list of Todoist projects.

        :return: .. schema:: todoist.TodoistProjectSchema(many=True)
        """
        return TodoistProjectSchema().dump(self._get_api().state['projects'], many=True)

    @action
    def get_items(self):
        """
        Get list of Todoist projects.

        :return .. schema:: todoist.TodoistItemSchema(many=True)
        """
        return TodoistItemSchema().dump(self._get_api().state['items'], many=True)

    @action
    def get_filters(self):
        """
        Get list of Todoist filters.

        :return: .. schema:: todoist.TodoistFilterSchema(many=True)
        """
        return TodoistFilterSchema().dump(self._get_api().state['filters'], many=True)

    @action
    def get_live_notifications(self):
        """
        Get list of Todoist live notifications.

        :return: .. schema:: todoist.TodoistLiveNotificationSchema(many=True)
        """
        return TodoistLiveNotificationSchema().dump(
            self._get_api().state['live_notifications'], many=True
        )

    @action
    def get_collaborators(self):
        """
        Get list of collaborators.

        :return: .. schema:: todoist.TodoistCollaboratorSchema(many=True)
        """
        return TodoistCollaboratorSchema().dump(
            self._get_api().state['collaborators'], many=True
        )

    @action
    def get_notes(self):
        """
        Get list of Todoist notes.

        :return: .. schema:: todoist.TodoistNoteSchema(many=True)
        """
        return TodoistNoteSchema().dump(self._get_api().state['notes'], many=True)

    @action
    def get_project_notes(self):
        """
        Get list of Todoist project notes.

        :return: .. schema:: todoist.TodoistProjectNoteSchema(many=True)
        """
        return TodoistProjectNoteSchema().dump(
            self._get_api().state['project_notes'], many=True
        )

    @action
    def add_item(self, content: str, project_id: Optional[int] = None, **kwargs):
        """
        Add a new item.
        """
        api = self._get_api()
        manager = todoist.managers.items.ItemsManager(api=api)
        item = manager.add(content, project_id=project_id, **kwargs)
        api.commit()
        return item.data

    @action
    def delete_item(self, item_id: int):
        """
        Delete an item by id.
        """
        api = self._get_api()
        manager = todoist.managers.items.ItemsManager(api=api)
        manager.delete(item_id)
        api.commit()

    @action
    def update_item(self, item_id: int, **kwargs):
        """
        Update an item by id.
        """
        api = self._get_api()
        manager = todoist.managers.items.ItemsManager(api=api)
        manager.update(item_id, **kwargs)
        api.commit()

    @action
    def complete_item(self, item_id: int):
        """
        Mark an item as done.
        """
        api = self._get_api()
        manager = todoist.managers.items.ItemsManager(api=api)
        manager.complete(item_id)
        api.commit()

    @action
    def uncomplete_item(self, item_id: int):
        """
        Mark an item as not done.
        """
        api = self._get_api()
        manager = todoist.managers.items.ItemsManager(api=api)
        manager.uncomplete(item_id)
        api.commit()

    @action
    def archive(self, item_id: int):
        """
        Archive an item by id.
        """
        api = self._get_api()
        manager = todoist.managers.items.ItemsManager(api=api)
        manager.archive(item_id)
        api.commit()

    @action
    def unarchive(self, item_id: int):
        """
        Un-archive an item by id.
        """
        api = self._get_api()
        manager = todoist.managers.items.ItemsManager(api=api)
        manager.unarchive(item_id)
        api.commit()

    @action
    def sync(self):
        """
        Sync/update info with the remote server.
        """
        api = self._get_api()
        api.sync()


# vim:sw=4:ts=4:et:
