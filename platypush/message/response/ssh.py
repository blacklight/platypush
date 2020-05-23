from platypush.message.response import Response


class SSHResponse(Response):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SSHKeygenResponse(SSHResponse):
    def __init__(self, fingerprint: str, key_file: str, pub_key_file: str, *args, **kwargs):
        super().__init__(*args, output={
            'fingerprint': fingerprint,
            'key_file': key_file,
            'pub_key_file': pub_key_file,
        }, **kwargs)


# vim:sw=4:ts=4:et:
