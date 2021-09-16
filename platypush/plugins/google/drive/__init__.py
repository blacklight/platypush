import io
import os
from typing import Optional, List, Union

from platypush.plugins import action
from platypush.plugins.google import GooglePlugin
from platypush.message.response.google.drive import GoogleDriveFile


class GoogleDrivePlugin(GooglePlugin):
    """
    Google Drive plugin.

    Requires:

        * **google-api-python-client** (``pip install google-api-python-client``)
        * **oauth2client** (``pip install oauth2client``)

    """

    scopes = ['https://www.googleapis.com/auth/drive',
              'https://www.googleapis.com/auth/drive.appfolder',
              'https://www.googleapis.com/auth/drive.photos.readonly']

    def __init__(self, *args, **kwargs):
        super().__init__(scopes=self.scopes, *args, **kwargs)

    def get_service(self, **kwargs):
        return super().get_service(service='drive', version='v3')

    # noinspection PyShadowingBuiltins
    @action
    def files(self,
              filter: Optional[str] = None,
              folder_id: Optional[str] = None,
              limit: Optional[int] = 100,
              drive_id: Optional[str] = None,
              spaces: Optional[Union[str, List[str]]] = None,
              order_by: Optional[Union[str, List[str]]] = None) -> Union[GoogleDriveFile, List[GoogleDriveFile]]:
        """
        Get the list of files.

        :param filter: Optional filter (default: None). See
            `Google Drive API docs <https://developers.google.com/drive/api/v3/search-files>`_ for
            the supported syntax.

        :param folder_id: Drive folder ID to search (default: get all files).
        :param limit: Maximum number of entries to be retrieves (default: 100).
        :param drive_id: Shared drive ID to search (default: None).
        :param spaces: Drive spaces to search. Supported values:

            - ``drive``
            - ``appDataFolder``
            - ``photos``

        :param order_by: Order the results by a specific attribute or list
            of attributes (default: None). Supported attributes:

                - ``createdTime``
                - ``folder``
                - ``modifiedByMeTime``
                - ``modifiedTime``
                - ``name``
                - ``name_natural``
                - ``quotaBytesUsed``
                - ``recency``
                - ``sharedWithMeTime``
                - ``starred``
                - ``viewedByMeTime``

            Attributes will be sorted in ascending order by default. You can change that by
            by appending "``desc``" separated by a space to the attribute you want in descending
            order - e.g. ``["folder", "createdTime desc", "modifiedTime desc"]``.
        """

        service = self.get_service()
        page_token = None
        files = []

        if isinstance(order_by, list):
            order_by = ','.join(order_by)
        if isinstance(spaces, list):
            spaces = ','.join(spaces)
        if folder_id:
            if not filter:
                filter = ''
            else:
                filter += ' '

            filter += "'{}' in parents".format(folder_id)

        while True:
            results = service.files().list(
                q=filter,
                driveId=drive_id,
                pageSize=limit,
                orderBy=order_by,
                fields="nextPageToken, files(id, name, kind, mimeType)",
                pageToken=page_token,
                spaces=spaces,
            ).execute()

            page_token = results.get('nextPageToken')
            files.extend([
                GoogleDriveFile(
                    id=f.get('id'),
                    name=f.get('name'),
                    type=f.get('kind').split('#')[1],
                    mime_type=f.get('mimeType'),
                ) for f in results.get('files', [])
            ])

            if not page_token or (limit and len(files) >= limit):
                break

        return files

    @action
    def get(self, file_id: str):
        """
        Get the information of a file on the Drive by file ID.
        :param file_id: File ID.
        """
        service = self.get_service()
        file = service.files().get(fileId=file_id).execute()
        return GoogleDriveFile(
            type=file.get('kind').split('#')[1],
            id=file.get('id'),
            name=file.get('name'),
            mime_type=file.get('mimeType'),
        )

    @action
    def upload(self,
               path: str,
               mime_type: Optional[str] = None,
               name: Optional[str] = None,
               description: Optional[str] = None,
               parents: Optional[List[str]] = None,
               starred: bool = False,
               target_mime_type: Optional[str] = None) -> GoogleDriveFile:
        """
        Upload a file to Google Drive.

        :param path: Path of the file to upload.
        :param mime_type: MIME type of the source file (e.g. "``image/jpeg``").
        :param name: Name of the target file. Default: same name as the source file.
        :param description: File description.
        :param parents: List of folder IDs that will contain the file (default: drive root).
        :param starred: If True, then the uploaded file will be marked as starred by the user.
        :param target_mime_type: Target MIME type. Useful if you want to e.g. import a CSV file as a Google Sheet
            (use "``application/vnd.google-apps.spreadsheet``), or an ODT file to a Google Doc
            (use "``application/vnd.google-apps.document``). See
            `the official documentation <https://developers.google.com/drive/api/v3/mime-types>`_ for a complete list
            of supported types.
        """
        # noinspection PyPackageRequirements
        from googleapiclient.http import MediaFileUpload

        path = os.path.abspath(os.path.expanduser(path))
        name = name or os.path.basename(path)
        metadata = {
            'name': name,
            'description': description,
            'parents': parents,
            'starred': starred,
        }

        if target_mime_type:
            metadata['mimeType'] = target_mime_type

        media = MediaFileUpload(path, mimetype=mime_type)
        service = self.get_service()
        file = service.files().create(
            body=metadata,
            media_body=media,
            fields='*'
        ).execute()

        return GoogleDriveFile(
            type=file.get('kind').split('#')[1],
            id=file.get('id'),
            name=file.get('name'),
            mime_type=file.get('mimeType'),
        )

    @action
    def download(self, file_id: str, path: str) -> str:
        """
        Download a Google Drive file locally.

        :param file_id: Path of the file to upload.
        :param path: Path of the file to upload.
        :return: The local file path.
        """
        # noinspection PyPackageRequirements
        from googleapiclient.http import MediaIoBaseDownload

        service = self.get_service()
        request = service.files().get_media(fileId=file_id)
        path = os.path.abspath(os.path.expanduser(path))
        if os.path.isdir(path):
            name = service.files().get(fileId=file_id).execute().get('name')
            path = os.path.join(path, name)

        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False

        while not done:
            status, done = downloader.next_chunk()
            self.logger.info('Download progress: {}%'.format(status.progress()))

        with open(path, 'wb') as f:
            f.write(fh.getbuffer().tobytes())
        return path

    @action
    def create(self,
               name: str,
               description: Optional[str] = None,
               mime_type: Optional[str] = None,
               parents: Optional[List[str]] = None,
               starred: bool = False) -> GoogleDriveFile:
        """
        Create a file.

        :param name: File name.
        :param description: File description.
        :param mime_type: File MIME type.
        :param parents: List of folder IDs that will contain the file (default: drive root).
        :param starred: If True then the file will be marked as starred.
        """
        metadata = {
            'name': name,
            'description': description,
            'parents': parents,
            'starred': starred,
        }

        if mime_type:
            metadata['mimeType'] = mime_type

        service = self.get_service()
        file = service.files().create(
            body=metadata,
            fields='*'
        ).execute()

        return GoogleDriveFile(
            type=file.get('kind').split('#')[1],
            id=file.get('id'),
            name=file.get('name'),
            mime_type=file.get('mimeType'),
        )

    @action
    def update(self,
               file_id: str,
               name: Optional[str] = None,
               description: Optional[str] = None,
               add_parents: Optional[List[str]] = None,
               remove_parents: Optional[List[str]] = None,
               mime_type: Optional[str] = None,
               starred: bool = None,
               trashed: bool = None) -> GoogleDriveFile:
        """
        Update the metadata or the content of a file.

        :param file_id: File ID.
        :param name: Set the file name.
        :param description: Set the file description.
        :param add_parents: Add the file to these parent folder IDs.
        :param remove_parents: Remove the file from these parent folder IDs.
        :param mime_type: Set the file MIME type.
        :param starred: Change the starred flag.
        :param trashed: Move/remove from trash.
        """
        metadata = {}
        if name:
            metadata['name'] = name
        if description is not None:
            metadata['description'] = description
        if add_parents:
            metadata['add_parents'] = add_parents
        if remove_parents:
            metadata['remove_parents'] = remove_parents
        if mime_type:
            metadata['mimeType'] = mime_type
        if starred is not None:
            metadata['starred'] = starred
        if trashed is not None:
            metadata['trashed'] = trashed

        service = self.get_service()
        file = service.files().update(
            fileId=file_id,
            body=metadata,
            fields='*'
        ).execute()

        return GoogleDriveFile(
            type=file.get('kind').split('#')[1],
            id=file.get('id'),
            name=file.get('name'),
            mime_type=file.get('mimeType'),
        )

    @action
    def delete(self, file_id: str):
        """
        Delete a file from Google Drive.
        :param file_id: File ID.
        """
        service = self.get_service()
        service.files().delete(fileId=file_id).execute()

    @action
    def copy(self, file_id: str) -> GoogleDriveFile:
        """
        Create a copy of a file.
        :param file_id: File ID.
        """
        service = self.get_service()
        file = service.files().copy(fileId=file_id).execute()
        return GoogleDriveFile(
            type=file.get('kind').split('#')[1],
            id=file.get('id'),
            name=file.get('name'),
            mime_type=file.get('mimeType'),
        )

    @action
    def empty_trash(self):
        """
        Empty the Drive bin.
        """
        service = self.get_service()
        service.files().emptyTrash()


# vim:sw=4:ts=4:et:
