import datetime
import dateutil.parser

from flask import abort, request, render_template, Blueprint

from platypush.backend.http.app import template_folder
from platypush.backend.http.app.utils import authenticate, authentication_ok
from platypush.config import Config


map_ = Blueprint('map', __name__, template_folder=template_folder)

# Declare routes list
__routes__ = [
    map_,
]

def parse_time(time_string):
    if not time_string:
        return None

    now = datetime.datetime.now()

    if time_string == 'now':
        return now.isoformat()
    if time_string == 'yesterday':
        return (now - datetime.timedelta(days=1)).isoformat()

    try:
        return dateutil.parser.parse(time_string).isoformat()
    except ValueError:
        pass

    m = re.match('([-+]?)([0-9]+)([dhms])', time_string)
    if not m:
        raise RuntimeError('Invalid time interval string representation: "{}"'.
                           format(time_string))

    time_delta = (-1 if m.group(1) == '-' else 1) * int(m.group(2))
    time_unit = m.group(3)

    if time_unit == 'd':
        params = { 'days': time_delta }
    elif time_unit == 'h':
        params = { 'hours': time_delta }
    elif time_unit == 'm':
        params = { 'minutes': time_delta }
    elif time_unit == 's':
        params = { 'seconds': time_delta }

    return (now + datetime.timedelta(**params)).isoformat()


@map_.route('/map', methods=['GET'])
def map():
    """
    Query parameters:
        start -- Map timeline start timestamp
        end   -- Map timeline end timestamp
        zoom  -- Between 1-20. Set it if you want to override the
            Google's API auto-zoom. You may have to set it if you are
            trying to embed the map into an iframe

    Supported values for `start` and `end`:
        - now
        - yesterday
        - -30s (it means '30 seconds ago')
        - -10m (it means '10 minutes ago')
        - -24h (it means '24 hours ago')
        - -7d  (it means '7 days ago')
        - 2018-06-04T17:39:22.742Z (ISO strings)

    Default: start=yesterday, end=now
    """

    if not authentication_ok(request): return authenticate()
    map_conf = (Config.get('backend.http') or {}).get('maps', {})
    if not map_conf:
        abort(500, 'The maps plugin is not configured in backend.http')

    api_key = map_conf.get('api_key')
    if not api_key:
        abort(500, 'Google Maps api_key not set in the maps configuration')

    start = parse_time(request.args.get('start', default='yesterday'))
    end = parse_time(request.args.get('end', default='now'))
    zoom = request.args.get('zoom', default=None)

    return render_template('map.html', config=map_conf, utils=HttpUtils,
                           start=start, end=end, zoom=zoom,
                           token=Config.get('token'), api_key=api_key,
                           websocket_port=get_websocket_port())


# vim:sw=4:ts=4:et:
