from flask import Blueprint, render_template

from platypush.backend.http.app import template_folder
from platypush.backend.http.app.utils import authenticate
from platypush.backend.http.utils import HttpUtils

index = Blueprint('index', __name__, template_folder=template_folder)

# Declare routes list
__routes__ = [
    index,
]


@index.route('/')
@authenticate()
def index_route():
    """Route to the main web panel"""
    return render_template('index.html', utils=HttpUtils)


@index.route('/login', methods=['GET'])
def login_route():
    """
    Login GET route. It simply renders the index template, which will
    redirect to the login page if the user is not authenticated.
    """
    return render_template('index.html', utils=HttpUtils)


@index.route('/register', methods=['GET'])
def register_route():
    """
    Register GET route. It simply renders the index template, which will
    redirect to the registration page if no users are present.
    """
    return render_template('index.html', utils=HttpUtils)


# vim:sw=4:ts=4:et:
