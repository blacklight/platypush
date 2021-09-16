import base64
import os

from platypush.plugins import Plugin, action


class DropboxPlugin(Plugin):
    """
    Plugin to manage a Dropbox account and its files and folders.

    Requires:

        * **dropbox** (``pip install dropbox``)
    """

    def __init__(self, access_token, **kwargs):
        """
        :param access_token: Dropbox API access token. You can get yours by creating an app on
            https://dropbox.com/developers/apps
        :type access_token: str
        """

        super().__init__(**kwargs)
        self.access_token = access_token
        self._dbx = None

    def _get_instance(self):
        """
        :rtype: :class:`dropbox.Dropbox`
        """
        # noinspection PyPackageRequirements
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

        :return: dict with the following attributes:
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

        :return: dict
        """

        dbx = self._get_instance()
        usage = dbx.users_get_space_usage()

        return {
            'used': usage.used,
            'allocated': usage.allocation.get_individual().allocated,
        }

    @action
    def list(self, folder=''):
        """
        Returns the files in a folder

        :param folder: Folder name (default: root)
        :type folder: str

        :return: dict
        """

        from dropbox.files import FileMetadata

        dbx = self._get_instance()
        files = dbx.files_list_folder(folder).entries
        entries = []

        for item in files:
            entry = {
                attr: getattr(item, attr)
                for attr in ['id', 'name', 'path_display', 'path_lower',
                             'parent_shared_folder_id', 'property_groups']
            }

            if item.sharing_info:
                entry['sharing_info'] = {
                    attr: getattr(item.sharing_info, attr)
                    for attr in ['no_access', 'parent_shared_folder_id', 'read_only',
                                 'shared_folder_id', 'traverse_only']
                }
            else:
                entry['sharing_info'] = {}

            if isinstance(item, FileMetadata):
                entry['client_modified'] = item.client_modified.isoformat()
                entry['server_modified'] = item.server_modified.isoformat()

                for attr in ['content_hash', 'has_explicit_shared_members', 'is_downloadable', 'rev', 'size']:
                    if hasattr(item, attr):
                        entry[attr] = getattr(item, attr)

            entries.append(entry)

        return entries

    @action
    def copy(self, from_path: str, to_path: str, allow_shared_folder=True, autorename=False,
             allow_ownership_transfer=False):
        """
        Copy a file or folder to a different location in the user's Dropbox. If the source path is a folder all
        its contents will be copied.

        :param from_path: Source path
        :param to_path: Destination path
        :param bool allow_shared_folder: If true, :meth:`files_copy` will copy
            contents in shared folder, otherwise
            ``RelocationError.cant_copy_shared_folder`` will be returned if
            ``from_path`` contains shared folder. This field is always true for
            :meth:`files_move`.
        :param bool autorename: If there's a conflict, have the Dropbox server
            try to autorename the file to avoid the conflict.
        :param bool allow_ownership_transfer: Allow moves by owner even if it
            would result in an ownership transfer for the content being moved.
            This does not apply to copies.
        """

        dbx = self._get_instance()
        dbx.files_copy_v2(from_path, to_path, allow_shared_folder=allow_shared_folder,
                          autorename=autorename, allow_ownership_transfer=allow_ownership_transfer)

    @action
    def move(self, from_path: str, to_path: str, allow_shared_folder=True, autorename=False,
             allow_ownership_transfer=False):
        """
        Move a file or folder to a different location in the user's Dropbox. If the source path is a folder all its
        contents will be moved.

        :param from_path: Source path
        :param to_path: Destination path
        :param bool allow_shared_folder: If true, :meth:`files_copy` will copy
            contents in shared folder, otherwise
            ``RelocationError.cant_copy_shared_folder`` will be returned if
            ``from_path`` contains shared folder. This field is always true for
            :meth:`files_move`.
        :param bool autorename: If there's a conflict, have the Dropbox server
            try to autorename the file to avoid the conflict.
        :param bool allow_ownership_transfer: Allow moves by owner even if it
            would result in an ownership transfer for the content being moved.
            This does not apply to copies.
        """

        dbx = self._get_instance()
        dbx.files_move_v2(from_path, to_path, allow_shared_folder=allow_shared_folder,
                          autorename=autorename, allow_ownership_transfer=allow_ownership_transfer)

    @action
    def delete(self, path: str):
        """
        Delete the file or folder at a given path. If the path is a folder, all its contents will be deleted too

        :param str path: Path to be removed
        """

        dbx = self._get_instance()
        dbx.files_delete_v2(path)

    @action
    def restore(self, path: str, rev: str):
        """
        Restore a specific revision of a file to the given path.

        :param str path: Path to be removed
        :param str rev: Revision ID to be restored
        """

        dbx = self._get_instance()
        dbx.files_restore(path, rev)

    @action
    def mkdir(self, path: str):
        """
        Create a folder at a given path.

        :param str path: Folder path
        """

        dbx = self._get_instance()
        dbx.files_create_folder_v2(path)

    @action
    def save(self, path: str, url: str):
        """
        Save a specified URL into a file in user's Dropbox. If the given path already exists, the file will be renamed
        to avoid the conflict (e.g. myfile (1).txt).

        :param path: Dropbox destination path
        :param url: URL to download
        """

        dbx = self._get_instance()
        dbx.files_save_url(path, url)

    def _file_download(self, path: str, download_path=None):
        dbx = self._get_instance()
        metadata, response = dbx.files_download(path)
        ret = self._parse_metadata(metadata)
        ret['encoding'] = response.encoding or response.apparent_encoding

        if download_path:
            if os.path.isdir(download_path):
                download_path = os.path.join(download_path, metadata.name)

            with open(download_path, 'wb') as f:
                f.write(response.content)
            ret['file'] = download_path
        else:
            if ret['encoding'] in ('ascii', 'unicode', 'utf-8'):
                ret['content'] = response.text
            else:
                ret['content'] = base64.encodebytes(response.content).decode().strip()

        return ret

    def _file_download_zip(self, path: str, download_path=None):
        dbx = self._get_instance()
        result, response = dbx.files_download_zip(path)
        ret = self._parse_metadata(result.metadata)

        if download_path:
            if os.path.isdir(download_path):
                download_path = os.path.join(download_path, result.metadata.name + '.zip')

            with open(download_path, 'wb') as f:
                f.write(response.content)
            ret['file'] = download_path
        else:
            ret['content'] = base64.encodebytes(response.content).decode().strip()

        return ret

    # noinspection PyShadowingBuiltins
    @action
    def download(self, path: str, download_path=None, zip=False):
        """
        Download a file or a zipped directory from a user's Dropbox.

        :param str path: Dropbox destination path
        :param str download_path: Destination path on the local machine (optional)
        :param bool zip: If set then the content will be downloaded in zip format (default: False)
        :rtype: dict
        :return: A dictionary with keys: ``('id', 'name', 'parent_shared_folder_id', 'path', 'size', 'encoding',
            'content_hash')``. If download_path is set 'file' is also returned. Otherwise 'content' will be returned.
            If it's a text file then 'content' will contain its string representation, otherwise its base64-encoded
            representation.
        """

        from dropbox.files import FolderMetadata

        if download_path:
            download_path = os.path.abspath(os.path.expanduser(download_path))

        dbx = self._get_instance()

        metadata = dbx.files_get_metadata(path)
        if isinstance(metadata, FolderMetadata):
            zip = True

        if zip:
            return self._file_download_zip(path, download_path)

        return self._file_download(path, download_path)

    @action
    def get_metadata(self, path: str):
        """
        Get the metadata of the specified path

        :param str path: Path to the resource
        :rtype dict:
        """

        dbx = self._get_instance()
        metadata = dbx.files_get_metadata(path)
        return self._parse_metadata(metadata)

    @staticmethod
    def _parse_metadata(metadata):
        from dropbox.files import FileMetadata, FolderMetadata

        ret = {
            'name': metadata.name,
            'parent_shared_folder_id': metadata.parent_shared_folder_id,
            'path': metadata.path_display,
        }

        if isinstance(metadata, FileMetadata):
            ret['type'] = 'file'
            ret['id'] = metadata.id
            ret['size'] = metadata.size
            ret['content_hash'] = metadata.content_hash
            ret['rev'] = metadata.rev
        elif isinstance(metadata, FolderMetadata):
            ret['type'] = 'folder'
            ret['id'] = metadata.id
            ret['shared_folder_id'] = metadata.shared_folder_id

        return ret

    @action
    def search(self, query: str, path='', start=0, max_results=100, content=False):
        """
        Searches for files and folders. Note: Recent changes may not immediately
        be reflected in search results due to a short delay in indexing.

        :param str path: The path in the user's Dropbox to search. Should probably be a folder.
        :param str query: The string to search for. The search string is split
            on spaces into multiple tokens. For file name searching, the last
            token is used for prefix matching (i.e. "bat c" matches "bat cave"
            but not "batman car").
        :param long start: The starting index within the search results (used for paging).
        :param long max_results: The maximum number of search results to return.
        :param content: Search also in files content (default: False)
        :rtype dict:
        :return: Dictionary with the following fields: ``('matches', 'start')``.
        """

        from dropbox.files import SearchMode

        dbx = self._get_instance()
        response = dbx.files_search(query=query, path=path, start=start, max_results=max_results,
                                    mode=SearchMode.filename_and_content if content else SearchMode.filename)

        results = [self._parse_metadata(match.metadata) for match in response.matches]

        return {
            'results': results,
            'start': response.start,
        }

    @action
    def upload(self, file=None, text=None, path='/', overwrite=False, autorename=False):
        """
        Create a new file with the contents provided in the request. Do not use this to upload a file larger than 150 MB

        :param str file: File to be uploaded
        :param str text: Text content to be uploaded
        :param str path: Path in the user's Dropbox to save the file.
        :param bool overwrite: If set, in case of conflict the file will be overwritten (default: append content)
        :param bool autorename: If there's a conflict, as determined by
            ``mode``, have the Dropbox server try to autorename the file to
            avoid conflict.
        :rtype dict:
        :return: Dictionary with the metadata of the uploaded file
        """

        from dropbox.files import WriteMode, FolderMetadata
        from dropbox.exceptions import ApiError

        dbx = self._get_instance()

        if file:
            file = os.path.abspath(os.path.expanduser(file))
            try:
                metadata = dbx.files_get_metadata(path)
                if isinstance(metadata, FolderMetadata):
                    path = '/'.join([path, os.path.basename(file)])
            except ApiError:
                pass

            with open(file, 'rb') as f:
                content = f.read()
        elif text:
            content = text.encode()
        else:
            raise SyntaxError('Please specify either a file or text to be uploaded')

        metadata = dbx.files_upload(content, path, autorename=autorename,
                                    mode=WriteMode.overwrite if overwrite else WriteMode.add)

        return self._parse_metadata(metadata)


# vim:sw=4:ts=4:et:
