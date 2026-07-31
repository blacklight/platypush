from flask import Blueprint, request, redirect, make_response

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

    if session_token:
        user, _ = user_manager.authenticate_user_session(session_token)[:2]
        if user:
            user_manager.delete_user_session(session_token)

    redirect_target = redirect(redirect_page, 302)  # lgtm [py/url-redirection]
    response = make_response(redirect_target)
    cookie_kwargs = {
        'expires': 0,
        'path': '/',
        'secure': request.is_secure,
        'samesite': 'Lax',
    }
    response.set_cookie('session_token', '', **cookie_kwargs)
    response.set_cookie('csrf_token', '', **cookie_kwargs)
    return response


# vim:sw=4:ts=4:et:
