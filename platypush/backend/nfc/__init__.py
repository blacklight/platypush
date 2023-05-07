import base64
import json

from platypush.backend import Backend
from platypush.message.event.nfc import (
    NFCTagDetectedEvent,
    NFCTagRemovedEvent,
    NFCDeviceConnectedEvent,
    NFCDeviceDisconnectedEvent,
)


class NfcBackend(Backend):
    """
    Backend to detect NFC card events from a compatible reader.

    Triggers:

        * :class:`platypush.message.event.nfc.NFCDeviceConnectedEvent` when an NFC reader/writer is connected
        * :class:`platypush.message.event.nfc.NFCDeviceDisconnectedEvent` when an NFC reader/writer is disconnected
        * :class:`platypush.message.event.nfc.NFCTagDetectedEvent` when an NFC tag is detected
        * :class:`platypush.message.event.nfc.NFCTagRemovedEvent` when an NFC tag is removed

    Requires:

        * **nfcpy** >= 1.0 (``pip install 'nfcpy>=1.0'``)
        * **ndef** (``pip install ndeflib``)

    Run the following to check if your device is compatible with nfcpy and the right permissions are set::

        python -m nfc

    """

    def __init__(self, device='usb', *args, **kwargs):
        """
        :param device: Address or ID of the device to be opened. Examples:

            * `'usb:003:009'` opens device 9 on bus 3
            * `'usb:003'` opens the first available device on bus 3
            * `'usb'` opens the first available USB device (default)
        """

        super().__init__(*args, **kwargs)

        self.device_id = device
        self._clf = None

    def _get_clf(self):
        import nfc

        if not self._clf:
            self._clf = nfc.ContactlessFrontend()
            self._clf.open(self.device_id)
            self.bus.post(NFCDeviceConnectedEvent(reader=self._get_device_str()))
            self.logger.info(
                'Initialized NFC reader backend on device {}'.format(
                    self._get_device_str()
                )
            )

        return self._clf

    def _get_device_str(self):
        return str(self._clf.device)

    def close(self):
        if self._clf:
            self._clf.close()
            self._clf = None
            self.bus.post(NFCDeviceDisconnectedEvent(reader=self._get_device_str()))

    @staticmethod
    def _parse_records(tag):
        from ndef.text import TextRecord
        from ndef.uri import UriRecord
        from ndef.smartposter import SmartposterRecord
        from ndef.deviceinfo import DeviceInformationRecord
        from ndef.wifi import WifiSimpleConfigRecord, WifiPeerToPeerRecord
        from ndef.bluetooth import BluetoothLowEnergyRecord, BluetoothEasyPairingRecord
        from ndef.signature import SignatureRecord

        records = []

        if not tag.ndef:
            return records

        for record in tag.ndef.records:
            r = {
                'record_type': record.type,
                'record_name': record.name,
            }

            if isinstance(record, TextRecord):
                try:
                    r = {
                        **r,
                        'type': 'json',
                        'value': json.loads(record.text),
                    }
                except ValueError:
                    r = {
                        **r,
                        'type': 'text',
                        'text': record.text,
                    }
            elif isinstance(record, UriRecord):
                r = {
                    **r,
                    'type': 'uri',
                    'uri': record.uri,
                    'iri': record.iri,
                }
            elif isinstance(record, SmartposterRecord):
                r = {
                    **r,
                    'type': 'smartposter',
                    **{
                        attr: getattr(record, attr)
                        for attr in [
                            'resource',
                            'titles',
                            'title',
                            'action',
                            'icon',
                            'icons',
                            'resource_size',
                            'resource_type',
                        ]
                    },
                }
            elif isinstance(record, DeviceInformationRecord):
                r = {
                    **r,
                    'type': 'device_info',
                    **{
                        attr: getattr(record, attr)
                        for attr in [
                            'vendor_name',
                            'model_name',
                            'unique_name',
                            'uuid_string',
                            'version_string',
                        ]
                    },
                }
            elif isinstance(record, WifiSimpleConfigRecord):
                r = {
                    **r,
                    'type': 'wifi_simple_config',
                    **{attr: record[attr] for attr in record.attribute_names()},
                }
            elif isinstance(record, WifiPeerToPeerRecord):
                r = {
                    **r,
                    'type': 'wifi_peer_to_peer',
                    **{attr: record[attr] for attr in record.attribute_names()},
                }
            elif isinstance(record, BluetoothEasyPairingRecord):
                r = {
                    **r,
                    'type': 'bluetooth_easy_pairing',
                    **{
                        attr: getattr(record, attr)
                        for attr in ['device_address', 'device_name', 'device_class']
                    },
                }
            elif isinstance(record, BluetoothLowEnergyRecord):
                r = {
                    **r,
                    'type': 'bluetooth_low_energy',
                    **{
                        attr: getattr(record, attr)
                        for attr in [
                            'device_address',
                            'device_name',
                            'role_capabilities',
                            'appearance',
                            'flags',
                            'security_manager_tk_value',
                            'secure_connections_confirmation_value',
                            'secure_connections_random_value',
                        ]
                    },
                }
            elif isinstance(record, SignatureRecord):
                r = {
                    **r,
                    'type': 'signature',
                    **{
                        attr: getattr(record, attr)
                        for attr in [
                            'version',
                            'signature_type',
                            'hash_type',
                            'signature',
                            'signature_uri',
                            'certificate_format',
                            'certificate_store',
                            'certificate_uri',
                            'secure_connections_random_value',
                        ]
                    },
                }
            else:
                r = {
                    **r,
                    'type': 'binary',
                    'data': base64.encodebytes(record.data).decode(),
                }

            records.append(r)

        return records

    @staticmethod
    def _parse_id(tag):
        return ''.join([('%02X' % c) for c in tag.identifier])

    def _on_connect(self):
        def callback(tag):
            if not tag:
                return False

            tag_id = self._parse_id(tag)
            records = self._parse_records(tag)
            self.bus.post(
                NFCTagDetectedEvent(
                    reader=self._get_device_str(), tag_id=tag_id, records=records
                )
            )
            return True

        return callback

    def _on_release(self):
        def callback(tag):
            tag_id = self._parse_id(tag)
            self.bus.post(
                NFCTagRemovedEvent(reader=self._get_device_str(), tag_id=tag_id)
            )

        return callback

    def run(self):
        super().run()

        while not self.should_stop():
            try:
                clf = self._get_clf()
                clf.connect(
                    rdwr={
                        'on-connect': self._on_connect(),
                        'on-release': self._on_release(),
                    }
                )
            finally:
                self.close()


# vim:sw=4:ts=4:et:
