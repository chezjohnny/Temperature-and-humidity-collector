#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Blueprint, g

from ..tools import templated, get_best_language, get_user
from flask import render_template, request, flash, redirect, url_for, session, g, abort, current_app
from .. import forms
from flaskext.login import login_user, login_required, logout_user, AnonymousUser
from flaskext.babel import gettext as _, refresh,  lazy_gettext as __
import hashlib

frontend = Blueprint('frontend', __name__, url_prefix='/<lang_code>')

#---------- Language support -------------
@frontend.url_defaults
def add_language_code(endpoint, values):
    values.setdefault('lang_code', get_best_language(getattr(g, 'lang_code', None)))

@frontend.url_value_preprocessor
def pull_lang_code(endpoint, values):
    if values and ('lang_code' in values):
        lang_code = values.pop('lang_code')
        g.lang_code = get_best_language(lang_code)
    else:
        g.lang_code = get_best_language()

#---------- Routes ------------
@frontend.route('/')
@templated('index.html')
def index():
    if not getattr(g, 'lang_code', None):
        abort(404)
    return dict(title=_("Welcome"), msg=_("You are on the first page!"))


@frontend.route("/login", methods=["GET", "POST"])
@templated('login.html')
def login():
    form = forms.LoginForm(csrf_enabled=False)
    if request.method == 'POST' and form.validate_on_submit():
        # login and validate the user...
        user = get_user(form.username.data, form.password.data)
        if user is None:
            flash(_("Bad username or password."), "error")
            return dict(form=form, value=_('Submit'))
        login_user(user)
        flash(_("Logged in successfully."), "info")
        return redirect(request.args.get("next") or url_for(".index"))
    return dict(form=form, value=_('Submit'))

@frontend.route('/logout')
def logout():
    flash(_('You were logged out'), "warning")
    logout_user()
    return redirect(request.args.get("next") or url_for('.index'))

@frontend.route('/admin')
@templated('index.html')
@login_required
def admin():
    return dict(title=_("Admin area"), msg=_("You are on a protected page!"))


@frontend.route('/lang/<lang>')
def set_language(lang):
    refresh()
    return redirect(request.args.get("next").replace(g.lang_code, lang) or url_for('.index').replace(g.lang_code, lang))


@frontend.route('/register', methods=['GET', 'POST'])
@templated('register.html')
def register():
    form = forms.RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        flash(_('Thanks for registering'), 'info')
        return redirect(url_for('login'))
    return dict(form=form, value=_('Register'))


#----------- Error handler -----------------
@frontend.app_errorhandler(404)
def page_not_found(e):
    lang = request.path.split('/')[1]
    if lang in current_app.config.get('SUPPORTED_LANG'):
        g.lang_code = lang
    else:
        g.lang_code = request.accept_languages.best_match(current_app.config.get('SUPPORTED_LANG'))
    return render_template('404.html', title=__("Page Not Found"), msg=__("What you were looking for is just not there.")), 404

