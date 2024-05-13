import os

from typing import Optional, Dict, Any, List

from platypush.plugins import Plugin, action
from platypush.schemas.cups import JobAddedSchema, PrinterSchema


class CupsPlugin(Plugin):
    """
    A plugin to interact with local and remote printers over a CUPS server.
    """

    def __init__(
        self,
        host: str = 'localhost',
        port: int = 631,
        printer: Optional[str] = None,
        **kwargs
    ):
        """
        :param host: CUPS host IP/name (default: localhost).
        :param port: CUPS port (default: 631).
        :param printer: Default printer name that should be used.
        """
        super().__init__(**kwargs)
        self.host = host
        self.port = port
        self.printer = printer

    def _get_connection(self, host: Optional[str] = None, port: Optional[int] = None):
        import cups

        connection = cups.Connection(host=host or self.host, port=port or self.port)
        return connection

    def _get_printer(self, printer: Optional[str] = None):
        printer = printer or self.printer
        assert printer, 'No printer specified nor default printer configured'
        return printer

    @action
    def get_printers(
        self, host: Optional[str] = None, port: Optional[int] = None
    ) -> List[dict]:
        """
        Get the list of printers registered on a CUPS server.

        :param host: CUPS server host IP/name (default: default configured ``host``).
        :param port: CUPS server port (default: default configured ``port``).
        :return: .. schema:: cups.PrinterSchema(many=True)
        """
        conn = self._get_connection(host, port)
        return PrinterSchema().dump(conn.getPrinters())

    @action
    def print_test_page(
        self,
        printer: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
    ) -> dict:
        """
        Print the CUPS test page.

        :param printer: Printer name (default: default configured ``printer``).
        :param host: CUPS server IP/name (default: default configured ``host``).
        :param port: CUPS server port (default: default configured ``port``).
        :return: .. schema:: cups.JobAddedSchema
        """
        conn = self._get_connection(host, port)
        printer = self._get_printer(printer)
        job_id = conn.printTestPage(printer)
        return dict(JobAddedSchema().dump({'printer': printer, 'job_id': job_id}))

    @action
    def print_file(
        self,
        filename: str,
        printer: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        title: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> dict:
        """
        Print a file.

        :param filename: Path to the file to print.
        :param printer: Printer name (default: default configured ``printer``).
        :param host: CUPS server IP/name (default: default configured ``host``).
        :param port: CUPS server port (default: default configured ``port``).
        :param title: Print title.
        :param options: Extra CUPS name->value options.
        :return: .. schema:: cups.JobAddedSchema
        """
        filename = os.path.abspath(os.path.expanduser(filename))
        conn = self._get_connection(host, port)
        printer = self._get_printer(printer)
        job_id = conn.printFile(
            printer, filename=filename, title=title or '', options=options or {}
        )
        return dict(JobAddedSchema().dump({'printer': printer, 'job_id': job_id}))

    @action
    def print_files(
        self,
        filenames: List[str],
        printer: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        title: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> dict:
        """
        Print a list of files.

        :param filenames: Paths to the files to print.
        :param printer: Printer name (default: default configured ``printer``).
        :param host: CUPS server IP/name (default: default configured ``host``).
        :param port: CUPS server port (default: default configured ``port``).
        :param title: Print title.
        :param options: Extra CUPS name->value options.
        :return: .. schema:: cups.JobAddedSchema
        """
        filenames = [os.path.abspath(os.path.expanduser(f)) for f in filenames]
        conn = self._get_connection(host, port)
        printer = self._get_printer(printer)
        job_id = conn.printFiles(
            printer, filenames=filenames, title=title or '', options=options or {}
        )
        return dict(JobAddedSchema().dump({'printer': printer, 'job_id': job_id}))

    @action
    def add_printer(
        self,
        name: str,
        ppd_file: str,
        info: str,
        location: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
    ):
        """
        Add a printer.

        :param name: Printer name - alphanumeric + underscore characters only.
        :param ppd_file: Path to the PPD file with the printer information and configuration.
        :param host: CUPS server IP/name (default: default configured ``host``).
        :param port: CUPS server port (default: default configured ``port``).
        :param info: Human-readable information about the printer.
        :param location: Human-readable printer location info.
        """
        conn = self._get_connection(host, port)
        ppd_file = os.path.abspath(os.path.expanduser(ppd_file))
        conn.addPrinter(name=name, filename=ppd_file, info=info, location=location)

    @action
    def delete_printer(
        self, printer: str, host: Optional[str] = None, port: Optional[int] = None
    ):
        """
        Delete a printer from a CUPS server.

        :param printer: Printer name.
        :param host: CUPS server IP/name (default: default configured ``host``).
        """
        conn = self._get_connection(host, port)
        conn.deletePrinter(printer)

    @action
    def enable_printer(
        self,
        printer: Optional[str],
        host: Optional[str] = None,
        port: Optional[int] = None,
    ):
        """
        Enable a printer on a CUPS server.

        :param printer: Printer name.
        :param host: CUPS server IP/name (default: default configured ``host``).
        :param port: CUPS server port (default: default configured ``port``).
        """
        conn = self._get_connection(host, port)
        printer = self._get_printer(printer)
        conn.enablePrinter(printer)

    @action
    def disable_printer(
        self,
        printer: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
    ):
        """
        Disable a printer on a CUPS server.

        :param printer: Printer name.
        :param host: CUPS server IP/name (default: default configured ``host``).
        :param port: CUPS server port (default: default configured ``port``).
        """
        conn = self._get_connection(host, port)
        printer = self._get_printer(printer)
        conn.disablePrinter(printer)

    @action
    def get_jobs(
        self, host: Optional[str] = None, port: Optional[int] = None
    ) -> Dict[int, Dict[str, Any]]:
        """
        Get the list of active jobs.

        :param host: CUPS server IP/name (default: default configured ``host``).
        :param port: CUPS server port (default: default configured ``port``).
        :return: A job_id -> job_info dict.
        """
        conn = self._get_connection(host, port)
        return conn.getJobs()

    @action
    def accept_jobs(
        self,
        printer: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
    ):
        """
        Start accepting jobs on a printer.

        :param printer: Printer name.
        :param host: CUPS server IP/name (default: default configured ``host``).
        :param port: CUPS server port (default: default configured ``port``).
        """
        conn = self._get_connection(host, port)
        printer = self._get_printer(printer)
        conn.acceptJobs(printer)

    @action
    def reject_jobs(
        self,
        printer: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
    ):
        """
        Start rejecting jobs on a printer.

        :param printer: Printer name.
        :param host: CUPS server IP/name (default: default configured ``host``).
        :param port: CUPS server port (default: default configured ``port``).
        """
        conn = self._get_connection(host, port)
        printer = self._get_printer(printer)
        conn.rejectJobs(printer)

    @action
    def cancel_job(
        self,
        job_id: int,
        purge_job: bool = False,
        host: Optional[str] = None,
        port: Optional[int] = None,
    ):
        """
        Cancel a printer job.

        :param job_id: Job ID to cancel.
        :param purge_job: Also remove the job from the server (default: False).
        :param host: CUPS server IP/name (default: default configured ``host``).
        :param port: CUPS server port (default: default configured ``port``).
        """
        conn = self._get_connection(host, port)
        conn.cancelJob(job_id, purge_job=purge_job)

    @action
    def move_job(
        self,
        job_id: int,
        source_printer_uri: str,
        target_printer_uri: str,
        host: Optional[str] = None,
        port: Optional[int] = None,
    ):
        """
        Move a job to another printer/URI.

        :param job_id: Job ID to cancel.
        :param source_printer_uri: Source printer URI.
        :param target_printer_uri: Target printer URI.
        :param host: CUPS server IP/name (default: default configured ``host``).
        :param port: CUPS server port (default: default configured ``port``).
        """
        conn = self._get_connection(host, port)
        conn.moveJob(
            printer_uri=source_printer_uri,
            job_id=job_id,
            job_printer_uri=target_printer_uri,
        )

    @action
    def finish_document(
        self,
        printer: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
    ):
        """
        Finish sending a document to a printer.

        :param printer: Printer name (default: default configured ``printer``).
        :param host: CUPS server IP/name (default: default configured ``host``).
        :param port: CUPS server port (default: default configured ``port``).
        """
        conn = self._get_connection(host, port)
        printer = self._get_printer(printer)
        conn.finishDocument(printer)

    @action
    def add_printer_to_class(
        self,
        printer_class: str,
        printer: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
    ):
        """
        Add a printer to a class.

        :param printer_class: Class name.
        :param printer: Printer name.
        :param host: CUPS server IP/name (default: default configured ``host``).
        :param port: CUPS server port (default: default configured ``port``).
        """
        conn = self._get_connection(host, port)
        printer = self._get_printer(printer)
        conn.addPrinterToClass(printer, printer_class)

    @action
    def delete_printer_from_class(
        self,
        printer_class: str,
        printer: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
    ):
        """
        Delete a printer from a class.

        :param printer_class: Class name.
        :param printer: Printer name.
        :param host: CUPS server IP/name (default: default configured ``host``).
        :param port: CUPS server port (default: default configured ``port``).
        """
        conn = self._get_connection(host, port)
        printer = self._get_printer(printer)
        conn.deletePrinterFromClass(printer, printer_class)

    @action
    def get_classes(
        self, host: Optional[str] = None, port: Optional[int] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get the list of classes on a CUPS server.

        :param host: CUPS server IP/name (default: default configured ``host``).
        :param port: CUPS server port (default: default configured ``port``).
        :return: dict - class_name -> class_info.
        """
        conn = self._get_connection(host, port)
        return conn.getClasses()


# vim:sw=4:ts=4:et:
