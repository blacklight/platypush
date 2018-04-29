import json
import serial

from platypush.message.response import Response

from .. import Plugin


class SerialPlugin(Plugin):
    def __init__(self, device, baud_rate=9600, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.device = device
        self.baud_rate = baud_rate


    def get_data(self):
        ser = serial.Serial(self.device, self.baud_rate)

        try: data = ser.readline().decode('utf-8').strip()
        finally: ser.close()

        try: data = json.loads(data)
        except: pass

        return Response(output=data)


# vim:sw=4:ts=4:et:

