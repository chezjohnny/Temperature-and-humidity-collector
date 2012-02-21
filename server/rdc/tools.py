#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Johnny Mariethoz <Johnny.Mariethoz@rero.ch>"
__version__ = "0.0.0"
__copyright__ = "Copyright (c) 2012 Rero, Johnny Mariethoz"
__license__ = "Internal Use Only"

from functools import wraps
from flask import request
from flask import render_template, g
from flaskext.login import UserMixin
from rdc import login_manager, app
import hashlib

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

class ConfigUser(UserMixin):
    def __init__(self):
        self.id = hashlib.md5('%s.%s' % (app.config.get('USERNAME'),
                    app.config.get('PASSWORD'))).hexdigest()

@login_manager.user_loader
def load_user(userid):
    user = ConfigUser()
    return user
