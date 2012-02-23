from flask import Flask, g, redirect, url_for
from flaskext.login import LoginManager
from flaskext.babel import Babel

import webtest.default_config
from frontend import frontend
from mobile import mobile
from tools import ConfigUser, get_best_language
from rpc import rpc_handler
from models import db

babel = Babel()
login_manager = LoginManager()




@login_manager.user_loader
def load_user(userid):
    user = ConfigUser()
    return user

def create_app():
    from rdc import rdc
    app = Flask(__name__)
    
    app.config.from_object(default_config.Config)
    app.config.from_envvar('WEBTEST_SETTINGS', silent=True)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
    rpc_handler.connect(app, '/rpc/api')

#-------- Login -------------
    login_manager.setup_app(app)
   
    app.register_blueprint(rdc, url_prefix='/rdc')
    login_manager.login_view = "rdc.login"
    
    db.init_app(app)

#-------- Translations ------
    babel.init_app(app)
    @babel.localeselector
    def get_locale():
        # if a user is logged in, use the locale from the user settings
        lang_code = getattr(g, 'lang_code', None)
        if lang_code is not None:
            return lang_code
        return get_best_language()
    return app




#-------- Routes ------------
#@app.route('/mobile')
#def redirect_language():
#    return redirect(url_for('mobile.index'))

#@app.route('/')
#def redirect_language():
#    return redirect(url_for('frontend.index'))
#
##-------- Blueprints ------------
#app.register_blueprint(mobile, url_prefix='/mobile/<lang_code>',
#        defaults={'lang_code': ''})
#app.register_blueprint(rdc, url_prefix='/rdc')
##app.register_blueprint(frontend, url_prefix='/')
#app.register_blueprint(frontend, url_prefix='/<lang_code>')

