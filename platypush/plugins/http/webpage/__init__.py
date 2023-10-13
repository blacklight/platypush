from dataclasses import dataclass
import datetime
from enum import Enum
import json
import os
import re
import subprocess
import tempfile
import textwrap
from typing import Iterable, Optional, Union
from urllib.parse import urlparse

from platypush.plugins import Plugin, action


@dataclass
class OutputFormat:
    """
    Definition of a supported output format.
    """

    name: str
    cmd_fmt: str
    extensions: Iterable[str] = ()


class OutputFormats(Enum):
    """
    Supported output formats.
    """

    HTML = OutputFormat('html', extensions=('html', 'htm'), cmd_fmt='html')
    # PDF will first be exported to HTML and then converted to PDF
    PDF = OutputFormat('pdf', extensions=('pdf',), cmd_fmt='html')
    TEXT = OutputFormat('text', extensions=('txt',), cmd_fmt='text')
    MARKDOWN = OutputFormat('markdown', extensions=('md',), cmd_fmt='markdown')

    @classmethod
    def parse(
        cls,
        type: Union[str, "OutputFormats"],  # pylint: disable=redefined-builtin
        outfile: Optional[str] = None,
    ) -> "OutputFormats":
        """
        Parse the format given a type argument and and output file name.
        """
        try:
            fmt = (
                getattr(OutputFormats, type.upper()) if isinstance(type, str) else type
            )
        except AttributeError as e:
            raise AssertionError(
                f'Unsupported output format: {type}. Supported formats: '
                + f'{[f.name for f in OutputFormats]}'
            ) from e

        by_extension = {ext.lower(): f for f in cls for ext in f.value.extensions}
        if outfile:
            fmt_by_ext = by_extension.get(os.path.splitext(outfile)[1].lower()[1:])
            if fmt_by_ext:
                return fmt_by_ext

        return fmt


class HttpWebpagePlugin(Plugin):
    """
    Plugin to handle and parse/simplify web pages.
    It used to use the Mercury Reader web API, but now that the API is discontinued this plugin is basically a
    wrapper around the `mercury-parser <https://github.com/postlight/mercury-parser>`_ JavaScript library.

    Requires:

        * The mercury-parser library installed (``npm install -g @postlight/mercury-parser``)

    """

    _mercury_script = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'mercury-parser.js'
    )

    @staticmethod
    def _parse(proc):
        """
        Runs the mercury-parser script and returns the result as a string.
        """
        with subprocess.Popen(proc, stdout=subprocess.PIPE, stderr=None) as parser:
            return parser.communicate()[0].decode()

    @staticmethod
    def _fix_relative_links(markdown: str, url: str) -> str:
        """
        Fix relative links to match the base URL of the page (Markdown only).
        """
        parsed_url = urlparse(url)
        base_url = f'{parsed_url.scheme}://{parsed_url.netloc}'
        return re.sub(r'(\[.+?])\((/.+?)\)', fr'\1({base_url}\2)', markdown)

    @action
    def simplify(
        self,
        url: str,
        type: Union[  # pylint: disable=redefined-builtin
            str, OutputFormats
        ] = OutputFormats.HTML,
        html: Optional[str] = None,
        outfile: Optional[str] = None,
        font_size: str = '19px',
        font_family: Union[str, Iterable[str]] = (
            '-apple-system',
            'Segoe UI',
            'Roboto',
            'Oxygen',
            'Ubuntu',
            'Cantarell',
            "Fira Sans",
            'Open Sans',
            'Droid Sans',
            'Helvetica Neue',
            'Helvetica',
            'Arial',
            'sans-serif',
        ),
    ):
        """
        Parse the readable content of a web page removing any extra HTML elements using Mercury.

        :param url: URL to parse.
        :param type: Output format. Supported types: ``html``, ``markdown``,
            ``text``, ``pdf`` (default: ``html``).
        :param html: Set this parameter if you want to parse some HTML content
            already fetched. Note that URL is still required by Mercury to
            properly style the output, but it won't be used to actually fetch
            the content.
        :param outfile: If set then the output will be written to the specified
            file. If the file extension is ``.pdf`` then the content will be
            exported in PDF format. If the output ``type`` is not specified
            then it can also be inferred from the extension of the output file.
        :param font_size: Font size to use for the output (default: 19px).
        :param font_family: Custom font family (or list of font families, in
            decreasing order) to use for the output. It only applies to HTML
            and PDF.
        :return: dict

        Example return payload outfile is not specified::

            {
                "url": <url>,
                "title": <page title>,
                "content": <page parsed content>
            }

        Example return payload if outfile is specified::

            {
                "url": <url>,
                "title": <page title>,
                "outfile": <output file absolute path>
            }

        """

        self.logger.info('Parsing URL %s', url)
        fmt = OutputFormats.parse(type=type, outfile=outfile)
        proc = ['node', self._mercury_script, url, fmt.value.cmd_fmt]
        tmp_file = None

        if html:
            with tempfile.NamedTemporaryFile('w+', delete=False) as f:
                tmp_file = f.name
                f.write(html)
                f.flush()
                proc.append(f.name)

        try:
            response = self._parse(proc)
        finally:
            if tmp_file:
                os.unlink(tmp_file)

        try:
            response = json.loads(response.strip())
        except Exception as e:
            raise RuntimeError(
                f'Could not parse JSON: {e}. Response: {response}'
            ) from e

        if fmt == OutputFormats.MARKDOWN:
            response['content'] = self._fix_relative_links(response['content'], url)

        self.logger.debug('Got response from Mercury API: %s', response)
        title = response.get(
            'title',
            (
                ('Published' if response.get('date_published') else 'Generated')
                + ' on '
                + (
                    response.get('date_published')
                    or datetime.datetime.now().isoformat()
                )
            ),
        )

        content = response.get('content', '')

        if not outfile:
            return {
                'url': url,
                'title': title,
                'content': content,
            }

        return self._process_outfile(
            url=url,
            fmt=fmt,
            title=title,
            content=content,
            outfile=outfile,
            font_size=font_size,
            font_family=tuple(
                font_family,
            )
            if isinstance(font_family, str)
            else tuple(font_family),
        )

    @staticmethod
    def _style_by_format(
        fmt: OutputFormats,
        font_size: str,
        font_family: Iterable[str],
    ) -> str:
        """
        :return: The CSS style to be used for the given output format.
        """
        style = textwrap.dedent(
            f'''
            ._parsed-content-container {{
                font-size: {font_size};
                font-family: {', '.join(f'"{f}"' for f in font_family)};
            }}

            ._parsed-content {{
                text-align: justify;
            }}

            pre {{
                white-space: pre-wrap;
            }}
            '''
        )

        if fmt == OutputFormats.HTML:
            style += textwrap.dedent(
                '''
                ._parsed-content-container {
                    margin: 1em;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                }

                ._parsed-content {
                    max-width: 800px;
                }

                h1 {
                    max-width: 800px;
                }
                '''
            )

        return style

    @classmethod
    def _process_outfile(
        cls,
        url: str,
        fmt: OutputFormats,
        title: str,
        content: str,
        outfile: str,
        font_size: str,
        font_family: Iterable[str],
    ):
        """
        Process the output file.

        :param url: URL to parse.
        :param fmt: Output format. Supported types: ``html``, ``markdown``,
            ``text``, ``pdf`` (default: ``html``).
        :param title: Page title.
        :param content: Page content.
        :param outfile: Output file path.
        :param font_size: Font size to use for the output (default: 19px).
        :param font_family: Custom font family (or list of font families, in
            decreasing order) to use for the output. It only applies to HTML
            and PDF.
        :return: dict
        """
        outfile = os.path.abspath(os.path.expanduser(outfile))
        style = cls._style_by_format(fmt, font_size, font_family)

        if fmt in {OutputFormats.HTML, OutputFormats.PDF}:
            content = textwrap.dedent(
                f'''
                <div class="_parsed-content-container">
                    <h1><a href="{url}" target="_blank">{title}</a></h1>
                    <div class="_parsed-content">{content}</div>
                </div>
                '''
            )

            if fmt == OutputFormats.PDF:
                content = textwrap.dedent(
                    f'''<html>
                            <head>
                                <style>{style}</style>
                                <title>{title}</title>
                            </head>
                            <body>
                              {content}
                            </body>
                        </html>
                    '''
                )
            else:
                content = textwrap.dedent(
                    f'''
                    <style>
                        {style}
                    </style>
                    {content}
                    '''
                )
        elif fmt == OutputFormats.MARKDOWN:
            content = f'# [{title}]({url})\n\n{content}'

        if fmt == OutputFormats.PDF:
            cls._process_pdf(content, outfile, style)
        else:
            with open(outfile, 'w', encoding='utf-8') as f:
                f.write(content)

        return {
            'url': url,
            'title': title,
            'outfile': outfile,
        }

    @staticmethod
    def _process_pdf(content: str, outfile: str, style: str):
        """
        Convert the given HTML content to a PDF document.

        :param content: Page content.
        :param outfile: Output file path.
        :param style: CSS style to use for the output.
        """
        import weasyprint

        try:
            from weasyprint.fonts import FontConfiguration  # pylint: disable
        except ImportError:
            from weasyprint.document import FontConfiguration

        font_config = FontConfiguration()
        css = [
            weasyprint.CSS(string=style, font_config=font_config),
        ]

        weasyprint.HTML(string=content).write_pdf(outfile, stylesheets=css)


# vim:sw=4:ts=4:et:
