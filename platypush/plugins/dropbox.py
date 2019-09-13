from platypush.plugins import Plugin, action


class DropboxPlugin(Plugin):
    """
    Plugin to manage a Dropbox account and its files and folders.

    Requires:

        * **dropbox** (``pip install dropbox``)
    """

    def __init__(self, access_token, **kwargs):
        """
        :param access_token: Dropbox API access token. You can get yours by creating an app on https://dropbox.com/developers/apps
        :type access_token: str
        """

        super().__init__(**kwargs)
        self.access_token = access_token
        self._dbx = None

    def _get_instance(self):
        import dropbox

        if not self._dbx:
            self._dbx = dropbox.Dropbox(self.access_token)

        return self._dbx

    @action
    def get_account(self, account_id=None):
        """
        Get the information about a linked Dropbox account

        :param account_id: account_id. If none is specified then it will retrieve the current user's account id
        :type account_id: str

        :returns: dict with the following attributes:
            account_id, name, email, email_verified, disabled, profile_photo_url, team_member_id
        """

        dbx = self._get_instance()

        if not account_id:
            acc = dbx.users_get_current_account()
        else:
            acc = dbx.users_get_account(account_id)

        return {
                'account_id': acc.account_id,
                'name': acc.name.display_name,
                'email': acc.email,
                'email_verified': acc.email_verified,
                'disabled': acc.disabled,
                'profile_photo_url': acc.profile_photo_url,
                'team_member_id': acc.team_member_id,
        }

    @action
    def get_usage(self):
        """
        Get the amount of allocated and used remote space

        :returns: dict
        """

        dbx = self._get_instance()
        usage = dbx.users_get_space_usage()

        return {
                'used': usage.used,
                'allocated': usage.allocation.get_individual().allocated,
        }

    @action
    def list_files(self, folder=''):
        """
        Returns the files in a folder

        :param folder: Folder name (default: root)
        :type folder: str

        :returns: dict
        """

        from dropbox.files import FolderMetadata, FileMetadata

        dbx = self._get_instance()
        files = dbx.files_list_folder(folder).entries
        entries = []

        for item in files:
            entry = {
                    attr: getattr(item, attr)
                    for attr in ['id', 'name', 'path_display', 'path_lower', 'parent_shared_folder_id', 'property_groups']
            }

            if item.sharing_info:
                entry['sharing_info'] = {
                    attr: getattr(item.sharing_info, attr)
                    for attr in ['no_access', 'parent_shared_folder_id', 'read_only', 'shared_folder_id', 'traverse_only']
                }
            else:
                entry['sharing_info'] = {}

            if isinstance(item, FileMetadata):
                entry['client_modified'] = item.client_modified.isoformat()
                entry['server_modified'] = item.server_modified.isoformat()

                for attr in ['content_hash', 'has_explicit_shared_members', 'is_downloadable', 'rev', 'size']:
                    entry[attr] = getattr(item, attr)

            entries.append(entry)

        return entries


# vim:sw=4:ts=4:et:
