import datetime

from flask import Blueprint, request, redirect, render_template, make_response, url_for

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
    redirect_page = request.args.get('redirect', '/')
    session_token = request.cookies.get('session_token')

    if session_token:
        user = user_manager.authenticate_user_session(session_token)
        if user:
            return redirect(redirect_page, 302)

    if request.form:
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember')
        session = user_manager.create_user_session(username=username, password=password,
                                                   expires_at=datetime.datetime.utcnow() + datetime.timedelta(days=1)
                                                   if not remember else None)

        if session:
            redirect_target = redirect(redirect_page, 302)
            response = make_response(redirect_target)
            response.set_cookie('session_token', session.session_token)
            return response

    return render_template('login.html', utils=HttpUtils)


# vim:sw=4:ts=4:et:
