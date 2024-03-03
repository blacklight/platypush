import base64
import mimetypes
import os

from email.encoders import encode_base64
from email.mime.application import MIMEApplication
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from platypush.plugins import action
from platypush.plugins.google import GooglePlugin


class GoogleMailPlugin(GooglePlugin):
    r"""
    GMail plugin. It allows you to programmatically compose and (TODO) get emails.

    To use this plugin:

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
                      'gmail.modify' \
                      <WORKDIR>/credentials/google/client_secret.json [--noauth_local_webserver]

           When launched with ``--noauth_local_webserver``, the script will
           start a local webserver and print a URL that should be opened in
           your browser. After authorizing the application, you may be
           prompted with a code that you should copy and paste back to the
           script. Otherwise, if you're running the script on a desktop, a
           browser window will be opened automatically.

    """

    scopes = ['https://www.googleapis.com/auth/gmail.modify']

    def __init__(self, *args, **kwargs):
        super().__init__(scopes=self.scopes, *args, **kwargs)

    @action
    def compose(self, sender, to, subject, body, files=None):
        """
        Compose a message.

        :param sender: Sender email/name
        :type sender: str

        :param to: Recipient email or comma-separated list of recipient emails
        :type to: str

        :param subject: Email subject
        :type subject: str

        :param body: Email body
        :type body: str

        :param files: Optional list of files to attach
        :type files: list
        """

        message = MIMEMultipart() if files else MIMEText(body)
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject

        if files:
            for file in files:
                msg = MIMEText(body)
                message.attach(msg)
                content_type, encoding = mimetypes.guess_type(file)

                if content_type is None or encoding is not None:
                    content_type = 'application/octet-stream'

                main_type, sub_type = content_type.split('/', 1)
                with open(file, 'rb') as fp:
                    content = fp.read()

                if main_type == 'text':
                    msg = MIMEText(str(content), _subtype=sub_type)
                elif main_type == 'image':
                    msg = MIMEImage(content, _subtype=sub_type)
                elif main_type == 'audio':
                    msg = MIMEAudio(content, _subtype=sub_type)
                elif main_type == 'application':
                    msg = MIMEApplication(
                        content, _subtype=sub_type, _encoder=encode_base64
                    )
                else:
                    msg = MIMEBase(main_type, sub_type)
                    msg.set_payload(content)

                filename = os.path.basename(file)
                msg.add_header('Content-Disposition', 'attachment', filename=filename)
                message.attach(msg)

        service = self.get_service('gmail', 'v1')
        body = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
        message = service.users().messages().send(userId='me', body=body).execute()

        return message

    @action
    def get_labels(self):
        """
        Returns the available labels on the GMail account
        """
        service = self.get_service('gmail', 'v1')
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        return labels


# vim:sw=4:ts=4:et:
