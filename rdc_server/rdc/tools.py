#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import request, current_app
from flask import render_template, g
from flask_login import UserMixin
import hashlib
from functools import wraps

#-------- Template decorator ----------------
def templated(template=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            template_name = template
            if template_name is None:
                template_name = request.endpoint \
                .replace('.', '/') + '.html'
            ctx = f(*args, **kwargs)
            if ctx is None:
                ctx = {}
            elif not isinstance(ctx, dict):
                return ctx
            return render_template(template_name, **ctx)
        return decorated_function
    return decorator

#-------- Login ----------------
class ConfigUser(UserMixin):
    def __init__(self):
        self.id = hashlib.md5('%s.%s' % (current_app.config.get('USERNAME'),
                    current_app.config.get('PASSWORD'))).hexdigest()

def get_user(user_name, password):
    current_user = ConfigUser()
    current_hash = hashlib.md5('%s.%s' % (user_name, password))
    if current_user.get_id() == current_hash.hexdigest():
        return ConfigUser()
    else:
        return None

#------ Translations ------------
def get_best_language(lang=None):
    if lang:
        if lang in current_app.config.get('SUPPORTED_LANG'):
            return lang
        return None
    return request.accept_languages.best_match(current_app.config.get('SUPPORTED_LANG'))


