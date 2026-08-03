from platypush.message.event import Event


class DialLaunchRequest(Event):
    """
    Posted by the Flask route to the main process to launch a DIAL app.

    ``reply_topic`` is used verbatim as the name of a Redis list (queue)
    where the main process pushes the reply; it should not contain
    arbitrary user input.
    """

    def __init__(
        self,
        app_id: str,
        raw_payload: str,
        reply_topic: str,
        **kwargs,
    ):
        super().__init__(
            app_id=app_id,
            raw_payload=raw_payload,
            reply_topic=reply_topic,
            **kwargs,
        )


class DialLaunchReply(Event):
    """
    Posted by the main process back to the Flask route after a launch attempt.

    ``reply_topic`` is used verbatim as the name of a Redis list (queue)
    where the reply is pushed.
    """

    def __init__(
        self,
        success: bool,
        reply_topic: str,
        run_id: str = '',
        error: str = '',
        client_error: bool = False,
        **kwargs,
    ):
        super().__init__(
            success=success,
            run_id=run_id,
            error=error,
            client_error=client_error,
            reply_topic=reply_topic,
            **kwargs,
        )


class DialStopRequest(Event):
    """
    Posted by the Flask route to the main process to stop a running DIAL app.

    ``reply_topic`` is used verbatim as the name of a Redis list (queue)
    where the main process pushes the reply.
    """

    def __init__(
        self,
        app_id: str,
        reply_topic: str,
        **kwargs,
    ):
        super().__init__(app_id=app_id, reply_topic=reply_topic, **kwargs)


class DialStopReply(Event):
    """
    Posted by the main process back to the Flask route after a stop attempt.

    ``reply_topic`` is used verbatim as the name of a Redis list (queue)
    where the reply is pushed.

    ``client_error`` mirrors the same field on :class:`DialLaunchReply`:
    when ``True`` the route should map the failure to a 4xx status
    (``404`` for unknown/not-running app, ``400`` for bad input) instead
    of a blanket ``500``.
    """

    def __init__(
        self,
        success: bool,
        reply_topic: str,
        error: str = '',
        client_error: bool = False,
        **kwargs,
    ):
        super().__init__(
            success=success,
            error=error,
            client_error=client_error,
            reply_topic=reply_topic,
            **kwargs,
        )
