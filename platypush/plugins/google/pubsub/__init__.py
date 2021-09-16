import json
import os

from platypush.plugins import Plugin, action


class GooglePubsubPlugin(Plugin):
    """
    Send messages over a Google pub/sub instance.
    You'll need a Google Cloud active project and a set of credentials to use this plugin:

        1. Create a project on the `Google Cloud console <https://console.cloud.google.com/projectcreate>`_ if
           you don't have one already.

        2. In the `Google Cloud API console <https://console.cloud.google.com/apis/credentials/serviceaccountkey>`_
           create a new service account key. Select "New Service Account", choose the role "Pub/Sub Editor" and leave
           the key type as JSON.

        3. Download the JSON service credentials file. By default platypush will look for the credentials file under
           ~/.credentials/platypush/google/pubsub.json.

    Requires:

        * **google-api-python-client** (``pip install google-api-python-client``)
        * **oauth2client** (``pip install oauth2client``)
        * **google-cloud-pubsub** (``pip install google-cloud-pubsub``)


    """

    publisher_audience = 'https://pubsub.googleapis.com/google.pubsub.v1.Publisher'
    subscriber_audience = 'https://pubsub.googleapis.com/google.pubsub.v1.Subscriber'
    default_credentials_file = os.path.join(os.path.expanduser('~'),
                                            '.credentials', 'platypush', 'google', 'pubsub.json')

    def __init__(self, credentials_file: str = default_credentials_file, **kwargs):
        """
        :param credentials_file: Path to the JSON credentials file for Google pub/sub (default:
            ~/.credentials/platypush/google/pubsub.json)
        """
        super().__init__(**kwargs)
        self.credentials_file = credentials_file
        self.project_id = self.get_project_id()

    def get_project_id(self):
        credentials = json.load(open(self.credentials_file))
        return credentials.get('project_id')

    def get_credentials(self, audience: str):
        # noinspection PyPackageRequirements
        from google.auth import jwt
        return jwt.Credentials.from_service_account_file(self.credentials_file, audience=audience)

    @action
    def send_message(self, topic: str, msg, **kwargs):
        """
        Sends a message to a topic

        :param topic: Topic/channel where the message will be delivered. You can either specify the full topic name in
            the format ``projects/<project_id>/topics/<topic_name>``, where ``<project_id>`` must be the ID of your
            Google Pub/Sub project, or just ``<topic_name>``  - in such case it's implied that you refer to the
            ``topic_name`` under the ``project_id`` of your service credentials.
        :param msg: Message to be sent. It can be a list, a dict, or a Message object
        :param kwargs: Extra arguments to be passed to .publish()
        """
        # noinspection PyPackageRequirements
        from google.cloud import pubsub_v1
        # noinspection PyPackageRequirements
        from google.api_core.exceptions import AlreadyExists

        credentials = self.get_credentials(self.publisher_audience)
        publisher = pubsub_v1.PublisherClient(credentials=credentials)

        if not topic.startswith('projects/{}/topics/'.format(self.project_id)):
            topic = 'projects/{}/topics/{}'.format(self.project_id, topic)

        try:
            publisher.create_topic(topic)
        except AlreadyExists:
            pass

        if isinstance(msg, int) or isinstance(msg, float):
            msg = str(msg)
        if isinstance(msg, dict) or isinstance(msg, list):
            msg = json.dumps(msg)
        if isinstance(msg, str):
            msg = msg.encode()

        publisher.publish(topic, msg, **kwargs)


# vim:sw=4:ts=4:et:
