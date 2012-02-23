#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flaskext.wtf import Form, BooleanField, TextField, PasswordField, validators
from flaskext.babel import lazy_gettext as __

#----------- Registration ---------------------
class RegistrationForm(Form):
    username = TextField(__('Username'), [validators.Length(min=4, max=25)])
    email = TextField(__('Email Address'), [validators.Length(min=6, max=35)])
    password = PasswordField(__('New Password'), [
        validators.Required(),
        validators.EqualTo('confirm', message=__('Passwords must match'))
    ])
    confirm = PasswordField(__('Repeat Password'))
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

#----------- Login ---------------------
class LoginForm(Form):
    username = TextField(__('Username'), [validators.Length(min=4, max=25)])
    password = PasswordField(__('New Password'), [
        validators.Required(),
    ])
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
