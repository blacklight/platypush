import json

from typing import Optional, List

from platypush.backend import Backend
from platypush.context import get_plugin
from platypush.message.event.google.pubsub import GooglePubsubMessageEvent
from platypush.utils import set_thread_name


class GooglePubsubBackend(Backend):
    """
    Subscribe to a list of topics on a Google Pub/Sub instance. See
        :class:`platypush.plugins.google.pubsub.GooglePubsubPlugin` for a reference on how to generate your
        project and credentials file.

    Triggers:

        * :class:`platypush.message.event.google.pubsub.GooglePubsubMessageEvent` when a new message is received on
          a subscribed topic.

    Requires:

        * **google-cloud-pubsub** (``pip install google-cloud-pubsub``)

    """

    def __init__(self, topics: List[str], credentials_file: Optional[str] = None, *args, **kwargs):
        """
        :param topics: List of topics to subscribe. You can either specify the full topic name in the format
            ``projects/<project_id>/topics/<topic_name>``, where ``<project_id>`` must be the ID of your
            Google Pub/Sub project, or just ``<topic_name>``  - in such case it's implied that you refer to the
            ``topic_name`` under the ``project_id`` of your service credentials.
        :param credentials_file: Path to the Pub/Sub service credentials file (default: value configured on the
            ``google.pubsub`` plugin or ``~/.credentials/platypush/google/pubsub.json``).
        """

        super().__init__(*args, **kwargs)
        self.topics = topics

        if credentials_file:
            self.credentials_file = credentials_file
        else:
            plugin = self._get_plugin()
            self.credentials_file = plugin.credentials_file

    @staticmethod
    def _get_plugin():
        return get_plugin('google.pubsub')

    def _message_callback(self, topic):
        def callback(msg):
            data = msg.data.decode()
            try:
                data = json.loads(data)
            except Exception as e:
                self.logger.debug('Not a valid JSON: {}: {}'.format(data, str(e)))

            msg.ack()
            self.bus.post(GooglePubsubMessageEvent(topic=topic, msg=data))

        return callback

    def run(self):
        # noinspection PyPackageRequirements
        from google.cloud import pubsub_v1
        # noinspection PyPackageRequirements
        from google.api_core.exceptions import AlreadyExists

        super().run()
        set_thread_name('GooglePubSub')
        plugin = self._get_plugin()
        project_id = plugin.get_project_id()
        credentials = plugin.get_credentials(plugin.subscriber_audience)
        subscriber = pubsub_v1.SubscriberClient(credentials=credentials)

        for topic in self.topics:
            if not topic.startswith('projects/{}/topics/'.format(project_id)):
                topic = 'projects/{}/topics/{}'.format(project_id, topic)
            subscription_name = '/'.join([*topic.split('/')[:2], 'subscriptions', topic.split('/')[-1]])

            try:
                subscriber.create_subscription(name=subscription_name, topic=topic)
            except AlreadyExists:
                pass

            subscriber.subscribe(subscription_name, self._message_callback(topic))

        self.wait_stop()


# vim:sw=4:ts=4:et:
