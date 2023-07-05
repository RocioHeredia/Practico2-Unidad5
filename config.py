import os
import secrets

dirbase = os.path.abspath(os.path.dirname(__file__))
database = os.path.join(dirbase, 'datos.db')
SQLALCHEMY_DATABASE_URI = f'sqlite:///{database}'
SECRET_KEY = secrets.token_urlsafe(32)
SQLALCHEMY_TRACK_MODIFICATIONS = False
