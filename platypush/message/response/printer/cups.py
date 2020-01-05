from typing import Optional, List

from platypush.message.response import Response


class PrinterResponse(Response):
    def __init__(self,
                 *args,
                 name: str,
                 printer_type: int,
                 info: str,
                 uri: str,
                 state: int,
                 is_shared: bool,
                 state_message: Optional[str] = None,
                 state_reasons: Optional[List[str]] = None,
                 location: Optional[str] = None,
                 uri_supported: Optional[str] = None,
                 make_and_model: Optional[str] = None,
                 **kwargs):
        super().__init__(*args, output={
            'name': name,
            'printer_type': printer_type,
            'info': info,
            'uri': uri,
            'state': state,
            'is_shared': is_shared,
            'state_message': state_message,
            'state_reasons': state_reasons,
            'location': location,
            'uri_supported': uri_supported,
            'make_and_model': make_and_model,
        }, **kwargs)


class PrintersResponse(Response):
    def __init__(self,
                 *args,
                 printers: List[PrinterResponse],
                 **kwargs):
        super().__init__(*args, output={p.output['name']: p.output for p in printers}, **kwargs)


class PrinterJobAddedResponse(Response):
    def __init__(self,
                 *args,
                 printer: str,
                 job_id: int,
                 **kwargs):
        super().__init__(*args, output={
            'printer': printer,
            'job_id': job_id,
        }, **kwargs)


# vim:sw=4:ts=4:et:
