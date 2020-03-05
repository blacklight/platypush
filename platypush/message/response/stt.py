from platypush.message.response import Response


class SpeechDetectedResponse(Response):
    def __init__(self, *args, speech: str, **kwargs):
        super().__init__(*args, output={
            'speech': speech
        }, **kwargs)


# vim:sw=4:ts=4:et:
