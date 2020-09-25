class CameraException(RuntimeError):
    pass


class CaptureAlreadyRunningException(CameraException):
    def __init__(self, device):
        super().__init__('A capturing session on the device {} is already running'.format(device))


# vim:sw=4:ts=4:et:
