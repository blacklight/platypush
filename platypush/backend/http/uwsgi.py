"""
uWSGI webapp entry point
"""

from platypush.backend.http.app import application

if __name__ == '__main__':
    application.run()


# vim:sw=4:ts=4:et:
