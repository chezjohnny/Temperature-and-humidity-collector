from flask import Flask, g, redirect, url_for
from flaskext.login import LoginManager

import default_config
from tools import ConfigUser, get_best_language
from rpc import rpc_handler
from models import db

login_manager = LoginManager()

@login_manager.user_loader
def load_user(userid):
    user = ConfigUser()
    return user

def create_app():
    from mobile import mobile
    app = Flask(__name__)
    
    app.config.from_object(default_config.Config)
    app.config.from_envvar('RDC_SETTINGS', silent=True)
    
    rpc_handler.connect(app, '/api')

#-------- Login -------------
   
    app.register_blueprint(mobile, url_prefix='/mobile')
    login_manager.setup_app(app)
    login_manager.login_view = "mobile.login"
    
    db.init_app(app)
    return app





#@app.route('/')
#def redirect_language():
#    return redirect(url_for('frontend.index'))
