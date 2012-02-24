class Config(object):
    DEBUG = True
    TESTING = True
    DATABASE_URI = 'sqlite://:memory:'
    USERNAME = "toto"
    PASSWORD = "toto"
    SECRET_KEY = 'change it'
    SUPPORTED_LANG = ['en','fr']
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'

