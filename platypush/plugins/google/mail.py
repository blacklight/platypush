import base64
import httplib2
import mimetypes
import os

from apiclient import discovery

from email.encoders import encode_base64
from email.mime.application import MIMEApplication
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from platypush.message.response import Response
from platypush.plugins.google import GooglePlugin


class GoogleMailPlugin(GooglePlugin):
    scopes = ['https://www.googleapis.com/auth/gmail.modify']

    def __init__(self, *args, **kwargs):
        super().__init__(scopes=self.scopes, *args, **kwargs)


    def compose(self, sender, to, subject, body, files=None):
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
                with open(file, 'rb') as fp: content = fp.read()

                if main_type == 'text':
                    msg = mimetypes.MIMEText(content, _subtype=sub_type)
                elif main_type == 'image':
                    msg = MIMEImage(content, _subtype=sub_type)
                elif main_type == 'audio':
                    msg = MIMEAudio(content, _subtype=sub_type)
                elif main_type == 'application':
                    msg = MIMEApplication(content, _subtype=sub_type,
                                          _encoder=encode_base64)
                else:
                    msg = MIMEBase(main_type, sub_type)
                    msg.set_payload(content)

                filename = os.path.basename(file)
                msg.add_header('Content-Disposition', 'attachment', filename=filename)
                message.attach(msg)

        service = self._get_service()
        body = { 'raw': base64.urlsafe_b64encode(message.as_bytes()).decode() }
        message = (service.users().messages().send(
            userId='me', body=body).execute())

        return Response(output=message)


    def get_labels(self):
        service = self._get_service()
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        return Response(output=labels)


    def _get_service(self):
        scope = self.scopes[0]
        credentials = self.credentials[scope]
        http = credentials.authorize(httplib2.Http())
        return discovery.build('gmail', 'v1', http=http, cache_discovery=False)


# vim:sw=4:ts=4:et:

