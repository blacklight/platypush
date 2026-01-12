from urllib.parse import unquote_plus

from flask import abort, request, Blueprint, Response

from platypush.backend.http.app import template_folder
from platypush.context import get_bus
from platypush.message.event.custom import CustomEvent

tidal = Blueprint('tidal', __name__, template_folder=template_folder)

# Declare routes list
__routes__ = [
    tidal,
]


@tidal.route('/tidal/login', methods=['GET', 'POST'])
def login_page():
    """
    This route can be used by the music.tidal plugin to perform the PKCE login
    flow.
    """

    if request.method == 'POST':
        url = request.form.get('url')
        if not url:
            abort(400, 'Expected "url" form parameter')

        url = unquote_plus(url)
        get_bus().post(CustomEvent('tidal/login_callback', url=url))

        return Response(
            """
            <html>
                <head>
                    <title>Tidal Login</title>
                </head>

                <body>
                    <h1>Tidal Login</h1>
                    <p>Login information received. You can now close this page.</p>
                </body>
            </html>
            """,
            mimetype='text/html',
        )

    url = request.args.get('url')
    if not url:
        abort(400, 'Expected "url" parameter')

    return Response(
        f"""
        <html>
            <head>
                <title>Tidal Login</title>
            </head>

            <body>
                <h1>Tidal Login</h1>
                <p>Please click the link below to login to Tidal:</p>
                <p><a href="{url}" target="_blank">{url}</a></p>
                <p>After logging in, please copy the URL you were redirected to and
                paste it into the text box below:</p>
                <form action="/tidal/login" method="POST">
                    <input type="text" name="url" size="100"/>
                    <input type="submit" value="Submit"/>
                </form>
            </body>
        </html>
        """,
        mimetype='text/html',
    )
