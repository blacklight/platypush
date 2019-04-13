import os
import requests
import time

from platypush.plugins import action
from platypush.plugins.http.request import Plugin


class HttpWebpagePlugin(Plugin):
    """
    Plugin to handle and parse/simplify web pages

    Requires:

        * **requests** (``pip install requests``)
        * **weasyprint** (``pip install weasyprint``), optional, for HTML->PDF conversion
    """

    def __init__(self, mercury_api_key=None, **kwargs):
        """
        :param mercury_api_key: If set then Mercury will be used to parse web pages content
        :type mercury_api_key: str
        """

        super().__init__(**kwargs)
        self.mercury_api_key = mercury_api_key

    @action
    def simplify(self, url, outfile=None):
        """
        Parse the content of a web page removing any extra elements using Mercury

        :param url: URL to parse
        :param outfile: If set then the output will be written to the specified file
            (supported formats: pdf, html, plain (default)). The plugin will guess
            the format from the extension
        :return: dict. Example if outfile is not specified::

            {
                "url": <url>,
                "title": <page title>,
                "content": <page parsed content>
            }

        Example if outfile is specified:

            {
                "url": <url>,
                "title": <page title>,
                "outfile": <output file absolute path>
            }
        """

        if not self.mercury_api_key:
            raise RuntimeError("mercury_api_key not set")

        self.logger.info('Parsing URL {}'.format(url))
        response = requests.get('https://mercury.postlight.com/parser',
                                params={'url': url},
                                headers={'x-api-key': self.mercury_api_key})

        if not response or not response.ok:
            raise RuntimeError("Unable to parse content for {}: {}".format(url, response.reason))

        if not len(response.text):
            raise RuntimeError("Empty response from Mercury API for URL {}".format(url))

        self.logger.info('Got response from Mercury API: {}'.format(response.json()))
        title = response.json().get('title', 'No_title_{}'.format(int(time.time())))
        content = '<body style="{body_style}"><h1>{title}</h1>{content}</body>'.\
            format(title=title, content=response.json()['content'],
                   body_style='font-size: 22px; font-family: Tahoma, Geneva, sans-serif')

        if not outfile:
            return {
                'url': url,
                'title': title,
                'content': content,
            }

        outfile = os.path.abspath(os.path.expanduser(outfile))

        if outfile.endswith('.pdf'):
            import weasyprint
            weasyprint.HTML(string=content).write_pdf(outfile)
        else:
            with open(outfile, 'w', encoding='utf-8') as f:
                f.write(content)

        return {
            'url': url,
            'title': title,
            'outfile': outfile,
        }


# vim:sw=4:ts=4:et:
