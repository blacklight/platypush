from flask import Blueprint, request, redirect, make_response, abort

from platypush.backend.http.app import template_folder
from platypush.user import UserManager

logout = Blueprint('logout', __name__, template_folder=template_folder)

# Declare routes list
__routes__ = [
    logout,
]


@logout.route('/logout', methods=['GET', 'POST'])
def logout_route():
    """Logout page"""
    user_manager = UserManager()
    redirect_page = request.args.get(
        'redirect', request.headers.get('Referer', '/login')
    )
    session_token = request.cookies.get('session_token')

    if not session_token:
        abort(417, 'Not logged in')

    user, _ = user_manager.authenticate_user_session(session_token)[:2]
    if not user:
        abort(403, 'Invalid session token')

    redirect_target = redirect(redirect_page, 302)  # lgtm [py/url-redirection]
    response = make_response(redirect_target)
    response.set_cookie('session_token', '', expires=0)
    return response


# vim:sw=4:ts=4:et:
