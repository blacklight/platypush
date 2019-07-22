import datetime
import re

from flask import Blueprint, request, redirect, render_template, make_response

from platypush.backend.http.app import template_folder
from platypush.backend.http.utils import HttpUtils
from platypush.user import UserManager

login = Blueprint('login', __name__, template_folder=template_folder)

# Declare routes list
__routes__ = [
    login,
]


@login.route('/login', methods=['GET', 'POST'])
def login():
    """ Login page """
    user_manager = UserManager()
    session_token = request.cookies.get('session_token')

    # redirect_page = request.args.get('redirect', request.headers.get('Referer', '/'))
    redirect_page = request.args.get('redirect')
    if not redirect_page:
        redirect_page = request.headers.get('Referer', '/')
    if re.search('(^https?://[^/]+)?/login[^?#]?', redirect_page):
        # Prevent redirect loop
        redirect_page = '/'

    if session_token:
        user, session = user_manager.authenticate_user_session(session_token)
        if user:
            return redirect(redirect_page, 302)

    if request.form:
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember')
        expires = datetime.datetime.utcnow() + datetime.timedelta(days=365) \
            if remember else None

        session = user_manager.create_user_session(username=username, password=password,
                                                   expires_at=expires)

        if session:
            redirect_target = redirect(redirect_page, 302)
            response = make_response(redirect_target)
            response.set_cookie('session_token', session.session_token, expires=expires)
            return response

    return render_template('login.html', utils=HttpUtils)


# vim:sw=4:ts=4:et:
