from platypush.message.response import Response


class TranslateResponse(Response):
    def __init__(self,
                 translated_text: str,
                 source_text: str,
                 detected_source_language: str,
                 *args,
                 **kwargs):
        super().__init__(*args, output={
            'translated_text': translated_text,
            'source_text': source_text,
            'detected_source_language': detected_source_language,
        }, **kwargs)


# vim:sw=4:ts=4:et:
