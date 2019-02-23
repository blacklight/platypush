"""
uWSGI webapp startup script
"""

from . import application

if __name__ == '__main__':
    application.run()


# vim:sw=4:ts=4:et:
