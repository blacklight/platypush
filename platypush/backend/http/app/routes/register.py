import datetime

from flask import Blueprint, request, redirect, render_template, make_response, url_for

from platypush.backend.http.app import template_folder
from platypush.backend.http.utils import HttpUtils
from platypush.user import UserManager

register = Blueprint('register', __name__, template_folder=template_folder)

# Declare routes list
__routes__ = [
    register,
]


@register.route('/register', methods=['GET', 'POST'])
def register():
    """ Registration page """
    user_manager = UserManager()
    redirect_page = request.args.get('redirect', '/')
    session_token = request.cookies.get('session_token')

    if session_token:
        user, session = user_manager.authenticate_user_session(session_token)
        if user:
            return redirect(redirect_page, 302)

    if request.form:
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        remember = request.form.get('remember')

        if password == confirm_password:
            user_manager.create_user(username=username, password=password)
            session = user_manager.create_user_session(username=username, password=password,
                                                       expires_at=datetime.datetime.utcnow() + datetime.timedelta(days=1)
                                                       if not remember else None)

            if session:
                redirect_target = redirect(redirect_page, 302)
                response = make_response(redirect_target)
                response.set_cookie('session_token', session.session_token)
                return response

    if user_manager.get_user_count() > 0:
        return redirect('/login?redirect=' + redirect_page, 302)

    return render_template('register.html', utils=HttpUtils)


# vim:sw=4:ts=4:et:
