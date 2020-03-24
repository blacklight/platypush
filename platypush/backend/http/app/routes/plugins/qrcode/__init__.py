import base64

from flask import abort, request, Blueprint, Response

from platypush.backend.http.app import template_folder
from platypush.context import get_plugin

qrcode = Blueprint('qrcode', __name__, template_folder=template_folder)

# Declare routes list
__routes__ = [
    qrcode,
]


@qrcode.route('/qrcode', methods=['GET'])
def generate_code():
    """
    This route can be used to generate a QR code given a ``content`` parameter.
    """

    from platypush.plugins.qrcode import QrcodePlugin
    content = request.args.get('content')
    if not content:
        abort(400, 'Expected content parmeter')

    plugin: QrcodePlugin = get_plugin('qrcode')
    response = plugin.generate(content, format='png').output
    data = base64.decodebytes(response['data'].encode())
    return Response(data, mimetype='image/png')


# vim:sw=4:ts=4:et:
