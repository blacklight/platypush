import os

from typing import Optional, Dict, Any, List

from platypush.message.response.printer.cups import PrinterResponse, PrintersResponse, PrinterJobAddedResponse
from platypush.plugins import Plugin, action


class PrinterCupsPlugin(Plugin):
    """
    A plugin to interact with a CUPS printer server.

    Requires:

        - **pycups** (``pip install pycups``)

    """

    def __init__(self, host: str = 'localhost', printer: Optional[str] = None, **kwargs):
        """
        :param host: CUPS host IP/name (default: localhost).
        :param printer: Default printer name that should be used.
        """
        super().__init__(**kwargs)
        self.host = host
        self.printer = printer

    def _get_connection(self, host: Optional[str] = None):
        # noinspection PyPackageRequirements
        import cups
        connection = cups.Connection(host=host or self.host)
        return connection

    def _get_printer(self, printer: Optional[str] = None):
        printer = printer or self.printer
        assert printer, 'No printer specified nor default printer configured'
        return printer

    @action
    def get_printers(self, host: Optional[str] = None) -> PrintersResponse:
        """
        Get the list of printers registered on a CUPS server.
        :param host: CUPS server host IP/name (default: default configured ``host``).
        :return: :class:`platypush.message.response.printer.cups.PrintersResponse`, as a name -> attributes dict.
        """
        conn = self._get_connection(host)
        return PrintersResponse(printers=[
            PrinterResponse(
                name=name,
                printer_type=printer.get('printer-type'),
                info=printer.get('printer-info'),
                uri=printer.get('device-uri'),
                state=printer.get('printer-state'),
                is_shared=printer.get('printer-is-shared'),
                state_message=printer.get('printer-state-message'),
                state_reasons=printer.get('printer-state-reasons', []),
                location=printer.get('printer-location'),
                uri_supported=printer.get('printer-uri-supported'),
                make_and_model=printer.get('printer-make-and-model'),
            )
            for name, printer in conn.getPrinters().items()
        ])

    @action
    def print_test_page(self, printer: Optional[str] = None, host: Optional[str] = None) -> PrinterJobAddedResponse:
        """
        Print the CUPS test page.

        :param printer: Printer name (default: default configured ``printer``).
        :param host: CUPS server IP/name (default: default configured ``host``).
        """
        conn = self._get_connection(host)
        printer = self._get_printer(printer)
        job_id = conn.printTestPage(printer)
        return PrinterJobAddedResponse(printer=printer, job_id=job_id)

    @action
    def print_file(self,
                   filename: str,
                   printer: Optional[str] = None,
                   host: Optional[str] = None,
                   title: Optional[str] = None,
                   options: Optional[Dict[str, Any]] = None) -> PrinterJobAddedResponse:
        """
        Print a file.

        :param filename: Path to the file to print.
        :param printer: Printer name (default: default configured ``printer``).
        :param host: CUPS server IP/name (default: default configured ``host``).
        :param title: Print title.
        :param options: Extra CUPS name->value options.
        """
        filename = os.path.abspath(os.path.expanduser(filename))
        conn = self._get_connection(host)
        printer = self._get_printer(printer)
        job_id = conn.printFile(printer, filename=filename, title=title or '', options=options or {})
        return PrinterJobAddedResponse(printer=printer, job_id=job_id)

    @action
    def print_files(self,
                    filenames: List[str],
                    printer: Optional[str] = None,
                    host: Optional[str] = None,
                    title: Optional[str] = None,
                    options: Optional[Dict[str, Any]] = None) -> PrinterJobAddedResponse:
        """
        Print a list of files.

        :param filenames: Paths to the files to print.
        :param printer: Printer name (default: default configured ``printer``).
        :param host: CUPS server IP/name (default: default configured ``host``).
        :param title: Print title.
        :param options: Extra CUPS name->value options.
        """
        filenames = [os.path.abspath(os.path.expanduser(f)) for f in filenames]
        conn = self._get_connection(host)
        printer = self._get_printer(printer)
        job_id = conn.printFiles(printer, filenames=filenames, title=title or '', options=options or {})
        return PrinterJobAddedResponse(printer=printer, job_id=job_id)

    @action
    def add_printer(self,
                    name: str,
                    ppd_file: str,
                    info: str,
                    location: Optional[str] = None,
                    host: Optional[str] = None):
        """
        Add a printer.

        :param name: Printer name - alphanumeric + underscore characters only.
        :param ppd_file: Path to the PPD file with the printer information and configuration.
        :param host: CUPS server IP/name (default: default configured ``host``).
        :param info: Human-readable information about the printer.
        :param location: Human-readable printer location info.
        """
        conn = self._get_connection(host)
        ppd_file = os.path.abspath(os.path.expanduser(ppd_file))
        # noinspection PyArgumentList
        conn.addPrinter(name=name, filename=ppd_file, info=info, location=location)

    @action
    def delete_printer(self, printer: str, host: Optional[str] = None):
        """
        Delete a printer from a CUPS server.

        :param printer: Printer name.
        :param host: CUPS server IP/name (default: default configured ``host``).
        """
        conn = self._get_connection(host)
        conn.deletePrinter(printer)

    @action
    def enable_printer(self, printer: Optional[str], host: Optional[str] = None):
        """
        Enable a printer on a CUPS server.

        :param printer: Printer name.
        :param host: CUPS server IP/name (default: default configured ``host``).
        """
        conn = self._get_connection(host)
        printer = self._get_printer(printer)
        conn.enablePrinter(printer)

    @action
    def disable_printer(self, printer: Optional[str] = None, host: Optional[str] = None):
        """
        Disable a printer on a CUPS server.

        :param printer: Printer name.
        :param host: CUPS server IP/name (default: default configured ``host``).
        """
        conn = self._get_connection(host)
        printer = self._get_printer(printer)
        conn.disablePrinter(printer)

    @action
    def get_jobs(self, host: Optional[str] = None) -> Dict[int, Dict[str, Any]]:
        """
        Get the list of active jobs.

        :param host: CUPS server IP/name (default: default configured ``host``).
        :return: A job_id -> job_info dict.
        """
        conn = self._get_connection(host)
        return conn.getJobs()

    @action
    def accept_jobs(self, printer: Optional[str] = None, host: Optional[str] = None):
        """
        Start accepting jobs on a printer.

        :param printer: Printer name.
        :param host: CUPS server IP/name (default: default configured ``host``).
        """
        conn = self._get_connection(host)
        printer = self._get_printer(printer)
        conn.acceptJobs(printer)

    @action
    def reject_jobs(self, printer: Optional[str] = None, host: Optional[str] = None):
        """
        Start rejecting jobs on a printer.

        :param printer: Printer name.
        :param host: CUPS server IP/name (default: default configured ``host``).
        """
        conn = self._get_connection(host)
        printer = self._get_printer(printer)
        conn.rejectJobs(printer)

    @action
    def cancel_job(self, job_id: int, purge_job: bool = False, host: Optional[str] = None):
        """
        Cancel a printer job.

        :param job_id: Job ID to cancel.
        :param purge_job: Also remove the job from the server (default: False).
        :param host: CUPS server IP/name (default: default configured ``host``).
        """
        conn = self._get_connection(host)
        conn.cancelJob(job_id, purge_job=purge_job)

    @action
    def move_job(self,
                 job_id: int,
                 source_printer_uri: str,
                 target_printer_uri: str,
                 host: Optional[str] = None):
        """
        Move a job to another printer/URI.

        :param job_id: Job ID to cancel.
        :param source_printer_uri: Source printer URI.
        :param target_printer_uri: Target printer URI.
        :param host: CUPS server IP/name (default: default configured ``host``).
        """
        conn = self._get_connection(host)
        conn.moveJob(printer_uri=source_printer_uri, job_id=job_id, job_printer_uri=target_printer_uri)

    @action
    def finish_document(self, printer: Optional[str] = None, host: Optional[str] = None):
        """
        Finish sending a document to a printer.

        :param printer: Printer name (default: default configured ``printer``).
        :param host: CUPS server IP/name (default: default configured ``host``).
        """
        conn = self._get_connection(host)
        printer = self._get_printer(printer)
        conn.finishDocument(printer)

    @action
    def add_printer_to_class(self,
                             printer_class: str,
                             printer: Optional[str] = None,
                             host: Optional[str] = None):
        """
        Add a printer to a class.

        :param printer_class: Class name.
        :param printer: Printer name.
        :param host: CUPS server IP/name (default: default configured ``host``).
        """
        conn = self._get_connection(host)
        printer = self._get_printer(printer)
        conn.addPrinterToClass(printer, printer_class)

    @action
    def delete_printer_from_class(self,
                                  printer_class: str,
                                  printer: Optional[str] = None,
                                  host: Optional[str] = None):
        """
        Delete a printer from a class.

        :param printer_class: Class name.
        :param printer: Printer name.
        :param host: CUPS server IP/name (default: default configured ``host``).
        """
        conn = self._get_connection(host)
        printer = self._get_printer(printer)
        conn.deletePrinterFromClass(printer, printer_class)

    @action
    def get_classes(self, host: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Get the list of classes on a CUPS server.

        :param host: CUPS server IP/name (default: default configured ``host``).
        :return: dict - class_name -> class_info.
        """
        conn = self._get_connection(host)
        return conn.getClasses()


# vim:sw=4:ts=4:et:
