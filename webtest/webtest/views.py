from webtest import app

from tools import templated, ConfigUser
from flask import render_template, request, flash, redirect, url_for, session, g
from webtest import forms
from flaskext.login import login_user, login_required, logout_user, AnonymousUser
from flaskext.babel import gettext, ngettext 
from webtest import babel

import hashlib

from flask import g, request
@babel.localeselector
def get_locale():
    lang = None
    if 'lang' in session:
        lang = session['lang']
    return lang

def get_user(user_name, password):
    current_user = ConfigUser()
    current_hash = hashlib.md5('%s.%s' % (user_name, password))
    if current_user.get_id() == current_hash.hexdigest():
        return ConfigUser()
    else:
        return None

@app.route("/login", methods=["GET", "POST"])
@templated()
def login():
    form = forms.LoginForm(csrf_enabled=False)
    if request.method == 'POST' and form.validate_on_submit():
        # login and validate the user...
        user = get_user(form.username.data, form.password.data)
        if user is None:
            flash("Bad username or password.", "error")
            return dict(form=form)
        login_user(user)
        flash("Logged in successfully.", "info")
        return redirect(request.args.get("next") or url_for("index"))
    return dict(form=form)

@app.route('/logout')
def logout():
    flash(gettext('You were logged out'), "warning")
    logout_user()
    return redirect(request.args.get("next") or url_for('index'))


@app.route('/')
@templated()
def index():
    return dict(title=gettext("Welcome"), msg=gettext("You are on the first page!"))

@app.route('/admin')
@templated('index.html')
@login_required
def admin():
    return dict(title="Admin area", msg="You are on a protected page!")


@app.route('/lang/<lang>')
def set_language(lang):
    if lang in ['en', 'fr']:
        session['lang'] = lang
    return redirect(request.args.get("next") or url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
@templated()
def register():
    form = forms.RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        flash('Thanks for registering', 'info')
        return redirect(url_for('login'))
    return dict(form=form)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
