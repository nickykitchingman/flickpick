import os
import secrets

WTF_CSRF_ENABLED = True
SECRET_KEY = secrets.token_urlsafe()
SECURITY_PASSWORD_SALT = secrets.SystemRandom().getrandbits(128)

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_ENGINE_OPTIONS = { 'pool_pre_ping': True, }
SQLALCHEMY_TRACK_MODIFICATIONS = True    