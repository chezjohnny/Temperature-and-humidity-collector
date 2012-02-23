#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Blueprint, g

from ..tools import templated, get_best_language
from flask import render_template, request, flash, redirect, url_for, session, g, abort, current_app
from webtest import forms
from flaskext.login import login_user, login_required, logout_user, AnonymousUser
from flaskext.babel import gettext as _, refresh,  lazy_gettext as __
import hashlib


mobile = Blueprint('mobile', __name__, url_prefix='/mobile/<lang_code>',
        template_folder='templates')


#---------- Language support -------------
@mobile.url_defaults
def add_language_code(endpoint, values):
    values.setdefault('lang_code', get_best_language(getattr(g, 'lang_code', None)))

@mobile.url_value_preprocessor
def pull_lang_code(endpoint, values):
    if values and ('lang_code' in values):
        lang_code = values.pop('lang_code')
        g.lang_code = get_best_language(lang_code)
    else:
        g.lang_code = get_best_language()
    print g.lang_code


#---------- Routes ------------
@mobile.route('/')
@templated()
def index():
    if not getattr(g, 'lang_code', None):
        abort(404)
    return dict(title=_("Welcome"), msg=_("You are on the first page!"))

@mobile.route('/test')
@templated('mobile/index.html')
def test():
    return dict(title=_("New page"), msg=_("You are on the second page!"))

@mobile.route('/lang/<lang>')
def set_language(lang):
    refresh()
    return redirect(request.args.get("next").replace(g.lang_code, lang) or url_for('.index').replace(g.lang_code, lang))

#----------- Error handler -----------------
@mobile.app_errorhandler(404)
def mobile_page_not_found(e):
    lang = request.path.split('/')[1]
    if lang in current_app.config.get('SUPPORTED_LANG'):
        g.lang_code = lang
    else:
        g.lang_code = request.accept_languages.best_match(current_app.config.get('SUPPORTED_LANG'))
    return render_template('mobile/404.html', title=__("Page Not Found"), msg=__("What you were looking for is just not there.")), 404

