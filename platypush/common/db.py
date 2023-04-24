from sqlalchemy import __version__

sa_version = tuple(map(int, __version__.split('.')))

if sa_version >= (1, 4, 0):
    from sqlalchemy.orm import declarative_base
else:
    from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
