import datetime
import enum
import json
from typing import List, Dict, Optional

import requests

from twilio.rest import Client
from twilio.base import values

from platypush.message import Message
from platypush.plugins import Plugin, action


class TwilioPhoneNumberType(enum.Enum):
    MOBILE = 'mobile'
    LOCAL = 'local'
    TOLL_FREE = 'toll_free'


class TwilioPlugin(Plugin):
    """
    The Twilio plugin allows you to send messages and WhatsApp texts and make programmable phone call by using a Twilio
    account. Note that some features may require a Premium account.

    Requires:

        * **twilio** (``pip install twilio``)
    """

    _api_base_url = 'https://api.twilio.com'

    def __init__(self,
                 account_sid: str,
                 auth_token: str,
                 address_sid: Optional[str] = None,
                 phone_number: Optional[str] = None,
                 address_book: Optional[Dict[str, str]] = None,
                 **kwargs):
        """
        :param account_sid: Account SID.
        :param auth_token: Account authentication token.
        :param address_sid: SID of the default physical address - required to register a new number in some countries.
        :param phone_number: Default phone number associated to the account to be used for messages and calls.
        :param address_book: ``name``->``phone_number`` mapping of contacts. You can use directly these names to send
            messages and make calls instead of the full phone number.
        """
        super().__init__(**kwargs)
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.address_sid = address_sid
        self.phone_number = phone_number
        self.address_book = address_book or {}
        self.client = Client(account_sid, auth_token)

    @action
    def get_available_phone_numbers(self, country: str, number_type: str) -> List[dict]:
        """
        Get a list of phone numbers of a certain type available for a certain country.

        :param country: Country code (e.g. ``US`` or ``NL``).
        :param number_type: Phone number type - e.g. ``mobile``, ``local`` or ``toll_free``.
        :return: A list of the available phone numbers with their properties and capabilities. Example:

            .. code-block:: json

                [
                  {
                    "friendly_name": "+311234567890",
                    "phone_number": "+311234567890",
                    "lata": null,
                    "rate_center": null,
                    "latitude": null,
                    "longitude": null,
                    "locality": null,
                    "region": null,
                    "postal_code": null,
                    "iso_country": "NL",
                    "address_requirements": "any",
                    "beta": false,
                    "capabilities": {
                      "voice": true,
                      "SMS": true,
                      "MMS": false,
                      "fax": false
                    }
                  }
              ]

        """
        phone_numbers = self.client.available_phone_numbers(country.upper()).fetch()
        resp = requests.get(self._api_base_url + phone_numbers.uri, auth=(self.account_sid, self.auth_token)).json()
        assert 'subresource_uris' in resp, 'No available phone numbers found for the country {}'.format(country)
        assert number_type in resp['subresource_uris'], 'No "{}" phone numbers available - available types: {}'.format(
            number_type, list(resp['subresource_uris'].keys())
        )

        resp = requests.get(self._api_base_url + resp['subresource_uris'][number_type],
                            auth=(self.account_sid, self.auth_token)).json()

        phone_numbers = resp['available_phone_numbers']
        assert len(phone_numbers), 'No phone numbers available'
        return phone_numbers

    @action
    def create_address(self,
                       customer_name: str,
                       street: str,
                       city: str,
                       region: str,
                       postal_code: str,
                       iso_country: str):
        # noinspection SpellCheckingInspection
        """
        Create a new address associated to your account.

        :param customer_name: Full name of the customer.
        :param street: Street name.
        :param city: City name.
        :param region: Region name.
        :param postal_code: Postal code.
        :param iso_country: ISO code of the country.
        :return: Details of the newly created address. Example:

            .. code-block:: json

                {
                  "account_sid": "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                  "city": "city",
                  "customer_name": "customer_name",
                  "date_created": "Tue, 18 Aug 2015 17:07:30 +0000",
                  "date_updated": "Tue, 18 Aug 2015 17:07:30 +0000",
                  "emergency_enabled": false,
                  "friendly_name": null,
                  "iso_country": "US",
                  "postal_code": "postal_code",
                  "region": "region",
                  "sid": "ADXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                  "street": "street",
                  "validated": false,
                  "verified": false,
                  "uri": "/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Addresses/ADXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.json"
                }

        """
        address = self.client.addresses.create(customer_name=customer_name,
                                               street=street,
                                               city=city,
                                               region=region,
                                               postal_code=postal_code,
                                               iso_country=iso_country)

        # noinspection PyProtectedMember
        return address._properties

    @action
    def register_phone_number(self,
                              phone_number: str,
                              friendly_name: Optional[str] = None,
                              address_sid: Optional[str] = None,
                              sms_url: Optional[str] = None,
                              sms_fallback_url: Optional[str] = None,
                              status_callback: Optional[str] = None,
                              voice_caller_id_lookup: bool = True,
                              voice_url: Optional[str] = None,
                              voice_fallback_url: Optional[str] = None,
                              area_code: Optional[str] = None) -> dict:
        # noinspection SpellCheckingInspection
        """
        Request to allocate a phone number on your Twilio account. The phone number should first be displayed as
        available in :meth:`.get_available_phone_numbers`.

        :param phone_number: Phone number to be allocated.
        :param friendly_name: A string used to identify your new phone number.
        :param address_sid: Address SID. NOTE: some countries may require you to specify a valid address in
            order to register a new phone number (see meth:`create_address`). If none is specified then the
            configured ``address_sid`` (if available) will be applied.
        :param sms_url: URL to call when an SMS is received.
        :param sms_fallback_url: URL to call when an error occurs on SMS delivery/receipt.
        :param status_callback: URL to call when a status change occurs.
        :param voice_caller_id_lookup: Whether to perform ID lookup for incoming caller numbers.
        :param voice_url: URL to call when the number receives a call.
        :param voice_fallback_url: URL to call when a call fails.
        :param area_code: Override the area code for the new number.
        :return: Status of the newly created number. Example:

            .. code-block:: json

                {
                  "account_sid": "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                  "address_requirements": "none",
                  "address_sid": "ADXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                  "api_version": "2010-04-01",
                  "beta": false,
                  "capabilities": {
                    "voice": true,
                    "sms": false,
                    "mms": true,
                    "fax": false
                  },
                  "date_created": "Thu, 30 Jul 2015 23:19:04 +0000",
                  "date_updated": "Thu, 30 Jul 2015 23:19:04 +0000",
                  "emergency_status": "Active",
                  "emergency_address_sid": "ADXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                  "friendly_name": "friendly_name",
                  "identity_sid": "RIXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                  "origin": "origin",
                  "phone_number": "+18089255327",
                  "sid": "PNXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                  "sms_application_sid": "APXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                  "sms_fallback_method": "GET",
                  "sms_fallback_url": "https://example.com",
                  "sms_method": "GET",
                  "sms_url": "https://example.com",
                  "status_callback": "https://example.com",
                  "status_callback_method": "GET",
                  "trunk_sid": null,
                  "uri": "/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/IncomingPhoneNumbers/PNXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.json",
                  "voice_application_sid": "APXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                  "voice_caller_id_lookup": false,
                  "voice_fallback_method": "GET",
                  "voice_fallback_url": "https://example.com",
                  "voice_method": "GET",
                  "voice_url": "https://example.com",
                  "bundle_sid": "BUXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                  "voice_receive_mode": "voice",
                  "status": "in-use"
                }

        """
        status = self.client.incoming_phone_numbers.create(phone_number=phone_number,
                                                           friendly_name=friendly_name,
                                                           sms_url=sms_url,
                                                           sms_fallback_url=sms_fallback_url,
                                                           status_callback=status_callback,
                                                           voice_caller_id_lookup=voice_caller_id_lookup,
                                                           voice_url=voice_url,
                                                           voice_fallback_url=voice_fallback_url,
                                                           area_code=area_code,
                                                           address_sid=address_sid or self.address_sid)

        # noinspection PyProtectedMember
        return status._properties

    @action
    def send_message(self,
                     body: str,
                     to: str,
                     from_: Optional[str] = None,
                     status_callback: Optional[str] = None,
                     max_price: Optional[str] = None,
                     attempt: Optional[int] = None,
                     validity_period: Optional[int] = None,
                     smart_encoded: bool = True,
                     media_url: Optional[str] = None) -> dict:
        # noinspection SpellCheckingInspection
        """
        Send an SMS/MMS.
        Note: WhatsApp messages are also supported (and free of charge), although the functionality is currently quite
        limited. Full support is only available to WhatsApp Business profiles and indipendent software vendors approved
        by WhatsApp. If that's not the case, you can send WhatsApp messages through the Twilio Test account/number -
        as of now the ``from_`` field should be ``whatsapp:+14155238886`` and the ``to`` field should be
        ``whatsapp:+<phone_number_here>``. More information `here <https://www.twilio.com/docs/whatsapp>`_.

        :param body: Message body.
        :param to: Recipient number or address book name.
        :param from_: Sender number. If none is specified then the default configured ``phone_number`` will be
            used if available.
        :param status_callback: The URL to call to send status information to the application.
        :param max_price: The total maximum price up to 4 decimal places in US dollars acceptable for the message to be
            delivered.
        :param attempt: Total numer of attempts made , this inclusive to send out the message.
        :param validity_period: The number of seconds that the message can remain in our outgoing queue.
        :param smart_encoded: Whether to detect Unicode characters that have a similar GSM-7 character and replace them.
        :param media_url: The URL of the media to send with the message.
        :return: A mapping representing the status of the delivery. Example:

            .. code-block:: json

                {
                  "account_sid": "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                  "api_version": "2010-04-01",
                  "body": "Sent from your Twilio trial account - It works!",
                  "date_created": "2020-08-17T16:32:09.341",
                  "date_updated": "2020-08-17T16:32:09.526",
                  "date_sent": null,
                  "direction": "outbound-api",
                  "error_code": null,
                  "error_message": null,
                  "from_": "+XXXXXXXXX",
                  "messaging_service_sid": null,
                  "num_media": "0",
                  "num_segments": "1",
                  "price": null,
                  "price_unit": "USD",
                  "sid": "XXXXXXXXXXXXX",
                  "status": "queued",
                  "subresource_uris": {
                    "media": "/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Messages/SMXXXXXXXXXXXXXXXXXX/Media.json"
                  },
                  "to": "+XXXXXXXXXXXXXX",
                  "uri": "/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Messages/SMXXXXXXXXXXXXXXXXXX.json"
                }

        """
        # noinspection SpellCheckingInspection
        assert from_ or self.phone_number, 'No valid sender phone number specified nor configured'
        if to in self.address_book:
            to = self.address_book[to]

        status = self.client.messages.create(
            body=body,
            from_=from_ or self.phone_number,
            to=to,
            media_url=media_url or values.unset,
            max_price=max_price or values.unset,
            attempt=str(attempt) if attempt else values.unset,
            status_callback=status_callback or values.unset,
            validity_period=str(validity_period) if validity_period else values.unset,
            smart_encoded=smart_encoded,
        )

        # noinspection PyProtectedMember
        return status._properties

    @action
    def list_messages(self,
                      to: Optional[str] = None,
                      from_: Optional[str] = None,
                      date_sent_before: Optional[str] = None,
                      date_sent: Optional[str] = None,
                      date_sent_after: Optional[str] = None,
                      limit: Optional[int] = None,
                      page_size: Optional[int] = None) -> List[dict]:
        # noinspection SpellCheckingInspection
        """
        List all messages matching the specified criteria.

        :param to: Recipient phone number or address book name.
        :param from_: Sender phone number.
        :param date_sent_before: Maximum date filter (ISO format: YYYYMMDD with or without time).
        :param date_sent: Date filter (ISO format: YYYYMMDD with or without time).
        :param date_sent_after: Minimum date filter (ISO format: YYYYMMDD with or without time).
        :param limit: Maximum number of messages to be returned.
        :param page_size: Maximum number of messages per page.
        :return: List of selected messages. Example:

            .. code-block:: json

                {
                  "account_sid": "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                  "api_version": "2010-04-01",
                  "body": "testing",
                  "date_created": "Fri, 24 May 2019 17:44:46 +0000",
                  "date_sent": "Fri, 24 May 2019 17:44:50 +0000",
                  "date_updated": "Fri, 24 May 2019 17:44:50 +0000",
                  "direction": "outbound-api",
                  "error_code": null,
                  "error_message": null,
                  "from": "+12019235161",
                  "messaging_service_sid": null,
                  "num_media": "0",
                  "num_segments": "1",
                  "price": "-0.00750",
                  "price_unit": "USD",
                  "sid": "SMded05904ccb347238880ca9264e8fe1c",
                  "status": "sent",
                  "subresource_uris": {
                    "media": "/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Messages/SMded05904ccb347238880ca9264e8fe1c/Media.json",
                    "feedback": "/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Messages/SMded05904ccb347238880ca9264e8fe1c/Feedback.json"
                  },
                  "to": "+18182008801",
                  "uri": "/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Messages/SMded05904ccb347238880ca9264e8fe1c.json"
                }

        """
        if to in self.address_book:
            to = self.address_book[to]

        # noinspection PyTypeChecker
        messages = self.client.messages.list(to=to, from_=from_,
                                             date_sent_before=datetime.datetime.fromisoformat(date_sent_before)
                                             if date_sent_before else None,
                                             date_sent_after=datetime.datetime.fromisoformat(date_sent_after)
                                             if date_sent_after else None,
                                             date_sent=datetime.datetime.fromisoformat(date_sent)
                                             if date_sent else None,
                                             limit=limit, page_size=page_size)

        # noinspection PyProtectedMember
        return json.loads(json.dumps([msg._properties for msg in messages], indent=2, cls=Message.Encoder))

    @action
    def get_message(self, message_sid: str) -> dict:
        """
        Get the details of a stored message.

        :param message_sid: Message SID to be retrieved.
        :return: Message with its properties - see :meth:`.send_message`.
        """
        msg = self.client.messages(message_sid).fetch()
        # noinspection PyProtectedMember
        return msg._properties

    @action
    def update_message(self, message_sid: str, body: str) -> dict:
        """
        Update/redact the body of a message.

        :param message_sid: Message SID to be updated.
        :param body: New message body.
        :return: Updated message with its properties - see :meth:`.send_message`.
        """
        msg = self.client.messages(message_sid).update(body)
        # noinspection PyProtectedMember
        return msg._properties

    @action
    def delete_message(self, message_sid: str):
        """
        Delete a send/received message.

        :param message_sid: Message SID to be deleted.
        """
        self.client.messages(message_sid).delete()

    @action
    def make_call(self,
                  twiml: str,
                  to: str,
                  from_: Optional[str] = None,
                  method: Optional[str] = None,
                  status_callback: Optional[str] = None,
                  status_callback_event: Optional[str] = None,
                  status_callback_method: Optional[str] = None,
                  fallback_url: Optional[str] = None,
                  fallback_method: Optional[str] = None,
                  send_digits: Optional[str] = None,
                  timeout: Optional[int] = 30,
                  record: bool = False,
                  recording_channels: Optional[int] = None,
                  recording_status_callback: Optional[str] = None,
                  recording_status_callback_method: Optional[str] = None,
                  recording_status_callback_event: Optional[str] = None,
                  sip_auth_username: Optional[str] = None,
                  sip_auth_password: Optional[str] = None,
                  caller_id: Optional[str] = None,
                  call_reason: Optional[str] = None) -> dict:
        # noinspection SpellCheckingInspection
        """
        Make an automated phone call from a registered Twilio number.

        :param twiml: TwiML containing the logic to be executed in the call (see https://www.twilio.com/docs/voice/twiml).
        :param to: Recipient phone number or address book name.
        :param from_: Registered Twilio phone number that will perform the call (default: default configured phone number).
        :param method: HTTP method to use to fetch TwiML if it's provided remotely.
        :param status_callback: The URL that should be called to send status information to your application.
        :param status_callback_event: The call progress events to be sent to the ``status_callback`` URL.
        :param status_callback_method: HTTP Method to use with status_callback.
        :param fallback_url: Fallback URL in case of error.
        :param fallback_method: HTTP Method to use with fallback_url.
        :param send_digits: The digits to dial after connecting to the number.
        :param timeout: Number of seconds to wait for an answer.
        :param record: Whether to record the call.
        :param recording_channels: The number of channels in the final recording.
        :param recording_status_callback: The URL that we call when the recording is available to be accessed.
        :param recording_status_callback_method: The HTTP method to use when calling the `recording_status_callback` URL.
        :param recording_status_callback_event: The recording status events that will trigger calls to the URL specified
            in `recording_status_callback`
        :param sip_auth_username: The username used to authenticate the caller making a SIP call.
        :param sip_auth_password: The password required to authenticate the user account specified in `sip_auth_username`.
        :param caller_id: The phone number, SIP address, or Client identifier that made this call. Phone numbers are in
            E.164 format (e.g., +16175551212). SIP addresses are formatted as `name@company.com`.
        :param call_reason: Reason for the call (Branded Calls Beta).
        :return: The call properties and details, as a dictionary. Example:

            .. code-block:: json

               {
                  "account_sid": "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                  "annotation": null,
                  "answered_by": null,
                  "api_version": "2010-04-01",
                  "caller_name": null,
                  "date_created": "Tue, 31 Aug 2010 20:36:28 +0000",
                  "date_updated": "Tue, 31 Aug 2010 20:36:44 +0000",
                  "direction": "inbound",
                  "duration": "15",
                  "end_time": "Tue, 31 Aug 2010 20:36:44 +0000",
                  "forwarded_from": "+141586753093",
                  "from": "+15017122661",
                  "from_formatted": "(501) 712-2661",
                  "group_sid": null,
                  "parent_call_sid": null,
                  "phone_number_sid": "PNXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                  "price": "-0.03000",
                  "price_unit": "USD",
                  "sid": "CAXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                  "start_time": "Tue, 31 Aug 2010 20:36:29 +0000",
                  "status": "completed",
                  "subresource_uris": {
                    "notifications": "/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Calls/CAXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Notifications.json",
                    "recordings": "/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Calls/CAXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Recordings.json",
                    "feedback": "/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Calls/CAXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Feedback.json",
                    "feedback_summaries": "/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Calls/FeedbackSummary.json",
                    "payments": "/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Calls/CAXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Payments.json"
                  },
                  "to": "+14155551212",
                  "to_formatted": "(415) 555-1212",
                  "trunk_sid": null,
                  "uri": "/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Calls/CAXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.json",
                  "queue_time": "1000"
               }

        """
        if to in self.address_book:
            to = self.address_book[to]

        call = self.client.calls.create(to=to,
                                        from_=from_ or self.phone_number,
                                        twiml=twiml,
                                        method=method,
                                        status_callback=status_callback,
                                        status_callback_event=status_callback_event,
                                        status_callback_method=status_callback_method,
                                        fallback_url=fallback_url,
                                        fallback_method=fallback_method,
                                        send_digits=send_digits,
                                        timeout=str(timeout) if timeout else None,
                                        record=record,
                                        recording_channels=str(recording_channels) if recording_channels else None,
                                        recording_status_callback=recording_status_callback,
                                        recording_status_callback_method=recording_status_callback_method,
                                        recording_status_callback_event=recording_status_callback_event,
                                        sip_auth_username=sip_auth_username,
                                        sip_auth_password=sip_auth_password,
                                        caller_id=caller_id,
                                        call_reason=call_reason)

        # noinspection PyProtectedMember
        return call._properties

    @action
    def list_calls(self,
                   to: Optional[str] = None,
                   from_: Optional[str] = None,
                   parent_call_sid: Optional[str] = None,
                   status: Optional[str] = None,
                   start_time_before: Optional[str] = None,
                   start_time: Optional[str] = None,
                   start_time_after: Optional[str] = None,
                   end_time_before: Optional[str] = None,
                   end_time: Optional[str] = None,
                   end_time_after: Optional[str] = None,
                   limit: Optional[int] = None,
                   page_size: Optional[int] = None) -> List[dict]:
        # noinspection SpellCheckingInspection
        """
        List the calls performed by the account, either the full list or those that match some filter.

        :param to: Phone number or Client identifier of calls to include
        :param from_: Phone number or Client identifier to filter `from` on
        :param parent_call_sid: Parent call SID to filter on
        :param  status: The status of the resources to read
        :param start_time_before: Only include calls that started on this date
        :param start_time: Only include calls that started on this date
        :param start_time_after: Only include calls that started on this date
        :param end_time_before: Only include calls that ended on this date
        :param end_time: Only include calls that ended on this date
        :param end_time_after: Only include calls that ended on this date
        :param limit: Upper limit for the number of records to return. list() guarantees
                          never to return more than limit.  Default is no limit
        :param page_size: Number of records to fetch per request, when not set will use
                              the default value of 50 records.  If no page_size is defined
                              but a limit is defined, list() will attempt to read the limit
                              with the most efficient page size, i.e. min(limit, 1000)
        :return: A list of dictionaries, each representing the information of a call. Example:

            .. code-block:: json

                [
                   {
                      "account_sid": "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                      "annotation": "billingreferencetag1",
                      "answered_by": "machine_start",
                      "api_version": "2010-04-01",
                      "caller_name": "callerid1",
                      "date_created": "Fri, 18 Oct 2019 17:00:00 +0000",
                      "date_updated": "Fri, 18 Oct 2019 17:01:00 +0000",
                      "direction": "outbound-api",
                      "duration": "4",
                      "end_time": "Fri, 18 Oct 2019 17:03:00 +0000",
                      "forwarded_from": "calledvia1",
                      "from": "+13051416799",
                      "from_formatted": "(305) 141-6799",
                      "group_sid": "GPXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                      "parent_call_sid": "CAXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                      "phone_number_sid": "PNXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                      "price": "-0.200",
                      "price_unit": "USD",
                      "sid": "CAXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                      "start_time": "Fri, 18 Oct 2019 17:02:00 +0000",
                      "status": "completed",
                      "subresource_uris": {
                        "feedback": "/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Calls/CAXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Feedback.json",
                        "feedback_summaries": "/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Calls/FeedbackSummary.json",
                        "notifications": "/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Calls/CAXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Notifications.json",
                        "recordings": "/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Calls/CAXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Recordings.json",
                        "payments": "/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Calls/CAXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Payments.json"
                      },
                      "to": "+13051913581",
                      "to_formatted": "(305) 191-3581",
                      "trunk_sid": "TKXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                      "uri": "/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Calls/CAXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.json",
                      "queue_time": "1000"
                  }
                ]

        """

        # noinspection PyTypeChecker
        call_list = self.client.calls.list(
            to=to,
            from_=from_,
            parent_call_sid=parent_call_sid,
            status=status,
            start_time_before=datetime.datetime.fromisoformat(start_time_before)
            if start_time_before else None,
            start_time=datetime.datetime.fromisoformat(start_time)
            if start_time else None,
            start_time_after=datetime.datetime.fromisoformat(start_time_after)
            if start_time_after else None,
            end_time_before=datetime.datetime.fromisoformat(end_time_before)
            if end_time_before else None,
            end_time=datetime.datetime.fromisoformat(end_time)
            if end_time else None,
            end_time_after=datetime.datetime.fromisoformat(end_time_after)
            if end_time_after else None,
            limit=limit,
            page_size=page_size
        )

        # noinspection PyProtectedMember
        return json.loads(json.dumps([call._properties for call in call_list], indent=2, cls=Message.Encoder))


# vim:sw=4:ts=4:et:
