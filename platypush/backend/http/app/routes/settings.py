from flask import Blueprint, request, render_template

from platypush.backend.http.app import template_folder, static_folder
from platypush.backend.http.app.utils import authenticate
from platypush.backend.http.utils import HttpUtils
from platypush.config import Config
from platypush.user import UserManager

settings = Blueprint('settings', __name__, template_folder=template_folder)

# Declare routes list
__routes__ = [
    settings,
]


@settings.route('/settings', methods=['GET'])
@authenticate()
def settings():
    """ Settings page """
    user_manager = UserManager()
    users = user_manager.get_users()
    return render_template('settings/index.html', utils=HttpUtils, users=users,
                           static_folder=static_folder, token=Config.get('token'))


# vim:sw=4:ts=4:et:
