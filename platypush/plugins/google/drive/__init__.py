import io
import os
from typing import Optional, List, Union

from platypush.plugins import action
from platypush.plugins.google import GooglePlugin
from platypush.schemas.google.drive import GoogleDriveFileSchema


class GoogleDrivePlugin(GooglePlugin):
    r"""
    Google Drive plugin.

        1. Create your Google application, if you don't have one already, on
           the `developers console <https://console.developers.google.com>`_.

        2. You may have to explicitly enable your user to use the app if the app
           is created in test mode. Go to "OAuth consent screen" and add your user's
           email address to the list of authorized users.

        3. Select the scopes that you want to enable for your application, depending
           on the integrations that you want to use.
           See https://developers.google.com/identity/protocols/oauth2/scopes
           for a list of the available scopes.

        4. Click on "Credentials", then "Create credentials" -> "OAuth client ID".

        5. Select "Desktop app", enter whichever name you like, and click "Create".

        6. Click on the "Download JSON" icon next to your newly created client ID.
           Save the JSON file under
           ``<WORKDIR>/credentials/google/client_secret.json``.

        7. If you're running the service on a desktop environment, then you
           can just start the application. A browser window will open and
           you'll be asked to authorize the application - you may be prompted
           with a warning because you are running a personal and potentially
           unverified application. After authorizing the application, the
           process will save the credentials under
           ``<WORKDIR>/credentials/google/<list,of,scopes>.json`` and proceed
           with the plugin initialization.

        8. If you're running the service on a headless environment, or you
           prefer to manually generate the credentials file before copying to
           another machine, you can run the following command:

                .. code-block:: bash

                  mkdir -p <WORKDIR>/credentials/google
                  python -m platypush.plugins.google.credentials \
                      'drive,drive.appfolder,drive.photos.readonly' \
                      <WORKDIR>/credentials/google/client_secret.json [--noauth_local_webserver]

           When launched with ``--noauth_local_webserver``, the script will
           start a local webserver and print a URL that should be opened in
           your browser. After authorizing the application, you may be
           prompted with a code that you should copy and paste back to the
           script. Otherwise, if you're running the script on a desktop, a
           browser window will be opened automatically.

    """

    scopes = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.appfolder',
        'https://www.googleapis.com/auth/drive.file',
    ]

    def __init__(self, **kwargs):
        super().__init__(scopes=self.scopes, **kwargs)

    def get_service(self, *_, **__):
        return super().get_service(service='drive', version='v3')

    @action
    def files(
        self,
        filter: Optional[str] = None,
        folder_id: Optional[str] = None,
        limit: Optional[int] = 100,
        drive_id: Optional[str] = None,
        spaces: Optional[Union[str, List[str]]] = None,
        order_by: Optional[Union[str, List[str]]] = None,
    ) -> List[dict]:
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

        :return: .. schema:: google.drive.GoogleDriveFileSchema(many=True)
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

            filter += f"'{folder_id}' in parents"

        while True:
            results = (
                service.files()
                .list(
                    q=filter,
                    driveId=drive_id,
                    pageSize=limit,
                    orderBy=order_by,
                    fields="nextPageToken, files(id, name, kind, mimeType)",
                    pageToken=page_token,
                    spaces=spaces,
                )
                .execute()
            )

            page_token = results.get('nextPageToken')
            files.extend(
                GoogleDriveFileSchema().dump(results.get('files', []), many=True)
            )

            if not page_token or (limit and len(files) >= limit):
                break

        return files

    @action
    def get(self, file_id: str):
        """
        Get the information of a file on the Drive by file ID.

        :param file_id: File ID.
        :return: .. schema:: google.drive.GoogleDriveFileSchema
        """
        service = self.get_service()
        file = service.files().get(fileId=file_id).execute()
        return GoogleDriveFileSchema().dump(file)

    @action
    def upload(
        self,
        path: str,
        mime_type: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        parents: Optional[List[str]] = None,
        starred: bool = False,
        target_mime_type: Optional[str] = None,
    ) -> dict:
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
        :return: The uploaded file metadata.

          .. schema:: google.drive.GoogleDriveFileSchema

        """
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
        file = (
            service.files()
            .create(body=metadata, media_body=media, fields='*')
            .execute()
        )

        return dict(GoogleDriveFileSchema().dump(file))

    @action
    def download(self, file_id: str, path: str) -> str:
        """
        Download a Google Drive file locally.

        :param file_id: Path of the file to upload.
        :param path: Path of the file to upload.
        :return: The local file path.
        """
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
            self.logger.info('Download progress: %s%%', status.progress())

        with open(path, 'wb') as f:
            f.write(fh.getbuffer().tobytes())

        return path

    @action
    def create(
        self,
        name: str,
        description: Optional[str] = None,
        mime_type: Optional[str] = None,
        parents: Optional[List[str]] = None,
        starred: bool = False,
    ) -> dict:
        """
        Create a file.

        :param name: File name.
        :param description: File description.
        :param mime_type: File MIME type.
        :param parents: List of folder IDs that will contain the file (default: drive root).
        :param starred: If True then the file will be marked as starred.
        :return: The created file metadata.

          .. schema:: google.drive.GoogleDriveFileSchema

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
        file = service.files().create(body=metadata, fields='*').execute()
        return dict(GoogleDriveFileSchema().dump(file))

    @action
    def update(
        self,
        file_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        add_parents: Optional[List[str]] = None,
        remove_parents: Optional[List[str]] = None,
        mime_type: Optional[str] = None,
        starred: Optional[bool] = None,
        trashed: Optional[bool] = None,
    ) -> dict:
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
        :return: The updated file metadata.

          .. schema:: google.drive.GoogleDriveFileSchema

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

        return dict(
            GoogleDriveFileSchema().dump(
                self.get_service()
                .files()
                .update(fileId=file_id, body=metadata, fields='*')
                .execute()
            )
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
    def copy(self, file_id: str) -> dict:
        """
        Create a copy of a file.

        :param file_id: File ID.
        :return: The copied file metadata.

          .. schema:: google.drive.GoogleDriveFileSchema

        """
        return dict(
            GoogleDriveFileSchema().dump(
                self.get_service().files().copy(fileId=file_id).execute()
            )
        )

    @action
    def empty_trash(self):
        """
        Empty the Drive bin.
        """
        service = self.get_service()
        service.files().emptyTrash()


# vim:sw=4:ts=4:et:
