from flask import Flask
from flaskext.login import LoginManager

from flaskext.sqlalchemy import SQLAlchemy
import rdc.default_config
import os
#tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
#app = Flask(__name__, template_dir=tmpl_dir)
app = Flask(__name__)

app.config.from_object(default_config.Config)
app.config.from_envvar('rdc_SETTINGS', silent=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.setup_app(app)
login_manager.login_view = "login"

import rdc.views
#import rdc.frontend
