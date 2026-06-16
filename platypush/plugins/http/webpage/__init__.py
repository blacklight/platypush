import datetime
import json
import os
import re
import shutil
import subprocess
import tempfile
import textwrap
from enum import Enum
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Iterable, Optional, Union
from urllib.parse import urlparse

from platypush.config import Config
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
    It uses the `Mozilla Readability library
    <https://github.com/mozilla/readability>`_ JavaScript library.
    """

    _plugin_dir = os.path.dirname(os.path.abspath(__file__))
    _parser_script = os.path.join(_plugin_dir, 'readability-parser.js')
    _npm_packages = ('@mozilla/readability', 'jsdom')

    _default_headers = {
        'User-Agent': (
            # Default user agent for a desktop browser
            'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 '
            '(KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1'
        ),
    }

    def __init__(self, *args, headers: Optional[dict] = None, **kwargs):
        """
        :param headers: Custom headers to be sent to the Readability API.
        """
        super().__init__(*args, **kwargs)
        self._headers = {**self._default_headers, **(headers or {})}
        self._ensure_node_deps()

    _block_tags = frozenset(
        (
            'p',
            'div',
            'br',
            'hr',
            'h1',
            'h2',
            'h3',
            'h4',
            'h5',
            'h6',
            'li',
            'ul',
            'ol',
            'blockquote',
            'pre',
            'article',
            'section',
            'header',
            'footer',
            'nav',
            'aside',
            'main',
            'figure',
            'figcaption',
            'table',
            'tr',
            'th',
            'td',
            'details',
            'summary',
        )
    )

    class _HtmlToTextParser(HTMLParser):
        """
        HTML parser that converts HTML to plain text, rendering links as
        ``link text [link url]``.
        """

        def __init__(self, block_tags: frozenset):
            super().__init__()
            self._chunks: list = []
            self._link_href: Optional[str] = None
            self._link_text: str = ''
            self._in_link: bool = False
            self._block_tags = block_tags

        def handle_starttag(self, tag, attrs):
            if tag == 'a':
                href = dict(attrs).get('href')
                if href:
                    self._in_link = True
                    self._link_href = href
                    self._link_text = ''
            elif tag in self._block_tags:
                self._chunks.append('\n')

        def handle_endtag(self, tag):
            if tag == 'a' and self._in_link:
                text = self._link_text.strip()
                if text and self._link_href:
                    self._chunks.append(f'{text} [{self._link_href}]')
                elif text:
                    self._chunks.append(text)
                self._in_link = False
                self._link_href = None
                self._link_text = ''
            elif tag in self._block_tags:
                self._chunks.append('\n')

        def handle_data(self, data):
            if self._in_link:
                self._link_text += data
            else:
                self._chunks.append(data)

        def get_text(self) -> str:
            return re.sub(r'\n{3,}', '\n\n', ''.join(self._chunks)).strip()

    @classmethod
    def _html_to_text(cls, html_content: str) -> str:
        """
        Convert HTML to plain text, rendering links as ``text [url]``.
        """
        parser = cls._HtmlToTextParser(cls._block_tags)
        parser.feed(html_content)
        return parser.get_text()

    @classmethod
    def _node_modules_dir(cls) -> str:
        """
        :return: The path to the node_modules directory under the
            application's working directory.
        """
        return os.path.join(Config.get_workdir(), 'http.webpage', 'node_modules')

    @classmethod
    def _ensure_node_deps(cls):
        """
        Ensure that the required npm packages are installed under the
        application's working directory.
        """
        node_modules = cls._node_modules_dir()
        node_dir = os.path.dirname(node_modules)
        missing = [
            pkg
            for pkg in cls._npm_packages
            if not os.path.isdir(os.path.join(node_modules, pkg))
        ]

        if not missing:
            return

        os.makedirs(node_dir, exist_ok=True)
        npm = shutil.which('npm')
        if not (npm):
            raise AssertionError(
                'npm is not installed or not found in PATH. '
                'It is required by the http.webpage plugin.'
            )

        subprocess.check_call(
            [npm, 'install', '--prefix', node_dir, *missing],
            stdout=subprocess.DEVNULL,
        )

    def _html_to_markdown(self, content: str, url: str) -> str:
        try:
            from markdownify import markdownify as md
        except ImportError:
            self.logger.warning(
                'Markdownify is not installed. '
                'The HTML content will not be converted to Markdown.'
            )

            return content

        return self._fix_relative_links(
            markdown=md(content, heading_style='ATX'),
            url=url,
        )

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
        *,
        type: Union[  # pylint: disable=redefined-builtin
            str, OutputFormats
        ] = OutputFormats.HTML,
        html: Optional[str] = None,
        headers: Optional[dict] = None,
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
        Parse the readable content of a web page removing any extra HTML elements using Readability.

        :param url: URL to parse.
        :param type: Output format. Supported types: ``html``, ``markdown``,
            ``text``, ``pdf`` (default: ``html``).
        :param html: Set this parameter if you want to parse some HTML content
            already fetched. Note that URL is still required by Readability to
            properly style the output, but it won't be used to actually fetch
            the content.
        :param headers: Custom headers to be sent to the Readability API.
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
        proc = ['node', self._parser_script, url, fmt.value.cmd_fmt]
        headers = {**self._headers, **(headers or {})}

        for k, v in headers.items():
            proc.extend((f'--{k}', v))

        tmp_file = None

        if html:
            with tempfile.NamedTemporaryFile('w+', delete=False) as f:
                tmp_file = f.name
                f.write(html)
                f.flush()
                proc.append(f.name)

        env = {**os.environ, 'NODE_PATH': self._node_modules_dir()}

        try:
            with subprocess.Popen(
                proc, stdout=subprocess.PIPE, stderr=None, env=env
            ) as parser:
                response = parser.communicate()[0].decode()
        finally:
            if tmp_file:
                os.unlink(tmp_file)

        try:
            response = json.loads(response.strip())
        except Exception as e:
            raise RuntimeError(
                f'Could not parse JSON: {e}. Response: {response}'
            ) from e

        if fmt == OutputFormats.TEXT:
            response['content'] = self._html_to_text(response['content'])
        elif fmt == OutputFormats.MARKDOWN:
            response['content'] = self._html_to_markdown(response['content'], url)

        self.logger.debug('Got response from Readability API: %s', response)
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
            font_family=(
                tuple(
                    font_family,
                )
                if isinstance(font_family, str)
                else tuple(font_family)
            ),
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
