import os
from os import environ


class Config(object):
    SECRET_KEY = '01643005C89EB7A158ED88540493A264A05EA82E475C2C8D151DFD390AAF4996'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DEFAULT_THEME = None
    # DEFAULT_THEME = "themes/dark"
    # DEFAULT_THEME = "themes/yeti"
    EIP_ENV = "vpn-prod"
    UPLOAD_FOLDER = "uploads"
    MAX_CONTENT_PATH = 52428800
    basedir = os.path.abspath(os.path.dirname(__file__))
    key = "jtCE)&{mq8X*26b"
    UPLOADED_PATH = os.path.join(basedir, 'uploads')
    DROPZONE_MAX_FILE_SIZE = 50000
    DROPZONE_TIMEOUT = 5 * 60 * 1000
    ENV = 'test'
    SYSTEM_ENV = 'test'



class ProductionConfig(Config):
    DEBUG = False

    # Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600
    SECRET_KEY = "jtCE)&{mq8X*26b"
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DebugConfig(Config):
    DEBUG = True


config_dict = {
    'Production': ProductionConfig,
    'Debug': DebugConfig
}
