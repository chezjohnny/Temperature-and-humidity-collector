# -*- coding: utf-8 -*-
from flask import Flask, g, redirect, url_for
from flask_login import LoginManager

import default_config
from tools import ConfigUser, get_best_language
from rpc import rpc_handler
from models import db
from flask_login import login_user, login_required, logout_user

login_manager = LoginManager()
login_manager.login_message = u"Vous devez être connecté pour accèder à la page de configuration"

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
    login_manager.init_app(app)
    login_manager.login_view = "mobile.login"
    
    db.init_app(app)
    return app




#@mobile.record_once
#def on_load(state):
#    login_manager.init_app(state.app)

