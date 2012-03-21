class Config(object):
    DEBUG = True
    TESTING = True
    DATABASE_URI = 'sqlite://:memory:'
    USERNAME = "toto"
    PASSWORD = "toto"
    SECRET_KEY = 'change it'
    SUPPORTED_LANG = ['en','fr']
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'
    SMTP_HOST_NAME = "smtp.gmail.com"
    SMTP_USER = 'change it'
    SMTP_PASSWD = 'change it'
    SMTP_PORT = 587
    EMAIL_FROM = 'change it'
    MODEM_SPEED = 9600
    MODEM_DEVICE = '/dev/ttyUSB2'
    MODEM_TIMEOUT = 5
