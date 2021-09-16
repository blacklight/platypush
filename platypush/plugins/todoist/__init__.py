import time

from typing import Optional

import todoist
import todoist.managers.items

from platypush.plugins import Plugin, action
from platypush.message.response.todoist import TodoistUserResponse, TodoistProjectsResponse, TodoistItemsResponse, \
    TodoistFiltersResponse, TodoistLiveNotificationsResponse, TodoistCollaboratorsResponse, TodoistNotesResponse, \
    TodoistProjectNotesResponse


class TodoistPlugin(Plugin):
    """
    Todoist integration.

    Requires:

        * **todoist-python** (``pip install todoist-python``)

    You'll also need a Todoist token. You can get it `here <https://todoist.com/prefs/integrations>`.
    """

    _sync_timeout = 60.0

    def __init__(self, api_token: str, **kwargs):
        """
        :param api_token: Todoist API token. You can get it `here <https://todoist.com/prefs/integrations>`.
        """

        super().__init__(**kwargs)
        self.api_token = api_token
        self._api = None
        self._last_sync_time = None

    def _get_api(self) -> todoist.TodoistAPI:
        if not self._api:
            self._api = todoist.TodoistAPI(self.api_token)

        if not self._last_sync_time or time.time() - self._last_sync_time > self._sync_timeout:
            self._api.sync()

        return self._api

    @action
    def get_user(self) -> TodoistUserResponse:
        """
        Get logged user info.
        """
        api = self._get_api()
        return TodoistUserResponse(**api.state['user'])

    @action
    def get_projects(self) -> TodoistProjectsResponse:
        """
        Get list of Todoist projects.
        """
        api = self._get_api()
        return TodoistProjectsResponse(api.state['projects'])

    @action
    def get_items(self) -> TodoistItemsResponse:
        """
        Get list of Todoist projects.
        """
        api = self._get_api()
        return TodoistItemsResponse(api.state['items'])

    @action
    def get_filters(self) -> TodoistFiltersResponse:
        """
        Get list of Todoist filters.
        """
        api = self._get_api()
        return TodoistFiltersResponse(api.state['filters'])

    @action
    def get_live_notifications(self) -> TodoistLiveNotificationsResponse:
        """
        Get list of Todoist live notifications.
        """
        api = self._get_api()
        return TodoistLiveNotificationsResponse(api.state['live_notifications'])

    @action
    def get_collaborators(self) -> TodoistCollaboratorsResponse:
        """
        Get list of collaborators.
        """
        api = self._get_api()
        return TodoistCollaboratorsResponse(api.state['collaborators'])

    @action
    def get_notes(self) -> TodoistNotesResponse:
        """
        Get list of Todoist notes.
        """
        api = self._get_api()
        return TodoistNotesResponse(api.state['notes'])

    @action
    def get_project_notes(self) -> TodoistProjectNotesResponse:
        """
        Get list of Todoist project notes.
        """
        api = self._get_api()
        return TodoistProjectNotesResponse(api.state['project_notes'])

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
