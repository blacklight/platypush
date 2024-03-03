import json
import os
from threading import RLock
from typing import Iterable, Optional

from google.auth import jwt
from google.cloud import pubsub_v1 as pubsub  # pylint: disable=no-name-in-module
from google.api_core.exceptions import AlreadyExists, NotFound

from platypush.config import Config
from platypush.message.event.google.pubsub import GooglePubsubMessageEvent
from platypush.plugins import RunnablePlugin, action


class GooglePubsubPlugin(RunnablePlugin):
    """
    Publishes and subscribes to Google Pub/Sub topics.

    You'll need a Google Cloud active project and a set of credentials to use
    this plugin:

        1. Create a project on the `Google Cloud console
           <https://console.cloud.google.com/projectcreate>`_ if you don't have
           one already.

        2. In the `Google Cloud API console
           <https://console.cloud.google.com/apis/credentials/serviceaccountkey>`_
           create a new service account key. Select "New Service Account", choose
           the role "Pub/Sub Editor" and leave the key type as JSON.

        3. Download the JSON service credentials file. By default Platypush
           will look for the credentials file under
           ``<WORKDIR>/credentials/google/pubsub.json``.

    """

    publisher_audience = 'https://pubsub.googleapis.com/google.pubsub.v1.Publisher'
    subscriber_audience = 'https://pubsub.googleapis.com/google.pubsub.v1.Subscriber'
    default_credentials_file = os.path.join(
        Config.get_workdir(), 'credentials', 'google', 'pubsub.json'
    )

    def __init__(
        self,
        credentials_file: str = default_credentials_file,
        topics: Iterable[str] = (),
        **kwargs,
    ):
        """
        :param credentials_file: Path to the JSON credentials file for Google
            pub/sub (default: ``~/.credentials/platypush/google/pubsub.json``)
        :param topics: List of topics to subscribe. You can either specify the
            full topic name in the format
            ``projects/<project_id>/topics/<topic_name>``, where
            ``<project_id>`` must be the ID of your Google Pub/Sub project, or
            just ``<topic_name>`` - in such case it's implied that you refer to
            the ``topic_name`` under the ``project_id`` of your service
            credentials.
        """
        super().__init__(**kwargs)
        self.credentials_file = credentials_file
        self.project_id = self.get_project_id()
        self.topics = topics
        self._subscriber: Optional[pubsub.SubscriberClient] = None
        self._subscriber_lock = RLock()

    def get_project_id(self):
        with open(self.credentials_file) as f:
            return json.load(f).get('project_id')

    def get_credentials(self, audience: str):
        return jwt.Credentials.from_service_account_file(
            self.credentials_file, audience=audience
        )

    def _norm_topic(self, topic: str):
        if not topic.startswith(f'projects/{self.project_id}/topics/'):
            topic = f'projects/{self.project_id}/topics/{topic}'
        return topic

    @action
    def publish(self, topic: str, msg, **kwargs):
        """
        Publish a message to a topic

        :param topic: Topic/channel where the message will be delivered. You
            can either specify the full topic name in the format
            ``projects/<project_id>/topics/<topic_name>``, where
            ``<project_id>`` must be the ID of your Google Pub/Sub project, or
            just ``<topic_name>`` - in such case it's implied that you refer to
            the ``topic_name`` under the ``project_id`` of your service
            credentials.
        :param msg: Message to be sent. It can be a list, a dict, or a Message object
        :param kwargs: Extra arguments to be passed to .publish()
        """
        credentials = self.get_credentials(self.publisher_audience)
        publisher = pubsub.PublisherClient(credentials=credentials)
        topic = self._norm_topic(topic)

        try:
            publisher.create_topic(name=topic)
        except AlreadyExists:
            self.logger.debug('Topic %s already exists', topic)

        if isinstance(msg, (int, float)):
            msg = str(msg)
        if isinstance(msg, (dict, list)):
            msg = json.dumps(msg)
        if isinstance(msg, str):
            msg = msg.encode()

        publisher.publish(topic, msg, **kwargs)

    @action
    def send_message(self, topic: str, msg, **kwargs):
        """
        Alias for :meth:`.publish`
        """
        self.publish(topic=topic, msg=msg, **kwargs)

    @action
    def subscribe(self, topic: str):
        """
        Subscribe to a topic.

        :param topic: Topic/channel where the message will be delivered. You
            can either specify the full topic name in the format
            ``projects/<project_id>/topics/<topic_name>``, where
            ``<project_id>`` must be the ID of your Google Pub/Sub project, or
            just ``<topic_name>`` - in such case it's implied that you refer to
            the ``topic_name`` under the ``project_id`` of your service
            credentials.
        """
        assert self._subscriber, 'Subscriber not initialized'
        topic = self._norm_topic(topic)
        subscription_name = '/'.join(
            [*topic.split('/')[:2], 'subscriptions', topic.split('/')[-1]]
        )

        try:
            self._subscriber.create_subscription(name=subscription_name, topic=topic)
        except AlreadyExists:
            self.logger.debug('Subscription %s already exists', subscription_name)

        self._subscriber.subscribe(subscription_name, self._message_callback(topic))

    @action
    def unsubscribe(self, topic: str):
        """
        Unsubscribe from a topic.

        :param topic: Topic/channel where the message will be delivered. You
            can either specify the full topic name in the format
            ``projects/<project_id>/topics/<topic_name>``, where
            ``<project_id>`` must be the ID of your Google Pub/Sub project, or
            just ``<topic_name>`` - in such case it's implied that you refer to
            the ``topic_name`` under the ``project_id`` of your service
            credentials.
        """
        assert self._subscriber, 'Subscriber not initialized'
        topic = self._norm_topic(topic)
        subscription_name = '/'.join(
            [*topic.split('/')[:2], 'subscriptions', topic.split('/')[-1]]
        )

        try:
            self._subscriber.delete_subscription(subscription=subscription_name)
        except NotFound:
            self.logger.debug('Subscription %s not found', subscription_name)

    def _message_callback(self, topic):
        def callback(msg):
            data = msg.data.decode()
            try:
                data = json.loads(data)
            except Exception as e:
                self.logger.debug('Not a valid JSON: %s: %s', data, e)

            msg.ack()
            self._bus.post(GooglePubsubMessageEvent(topic=topic, msg=data))

        return callback

    def main(self):
        credentials = self.get_credentials(self.subscriber_audience)
        with self._subscriber_lock:
            self._subscriber = pubsub.SubscriberClient(credentials=credentials)

        for topic in self.topics:
            self.subscribe(topic=topic)

        self.wait_stop()
        with self._subscriber_lock:
            self._close()

    def _close(self):
        with self._subscriber_lock:
            if self._subscriber:
                try:
                    self._subscriber.close()
                except Exception as e:
                    self.logger.debug('Error while closing the subscriber: %s', e)

                self._subscriber = None

    def stop(self):
        self._close()
        super().stop()


# vim:sw=4:ts=4:et:
