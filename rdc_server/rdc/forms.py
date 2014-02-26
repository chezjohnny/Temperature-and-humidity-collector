#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_wtf import Form, validators
from wtforms.validators import NumberRange, Length, Required
from wtforms.fields import BooleanField, TextField, PasswordField, DecimalField

#----------- Registration ---------------------
class ConfigurationForm(Form):

    enabled = BooleanField('Actif')
    is_visible = BooleanField('Visible')
    alert_warning_value = DecimalField('Alerte',
            [NumberRange(min=-30, max=30, message=u"La valeur doit être entre -30 et 30")])
    alert_critical_value = DecimalField('Alerte Critique',
            [NumberRange(min=-30, max=30, message=u"La valeur doit être entre -30 et 30")])
    notifiers = TextField('Notifications')
    def __init__(self, *args, **kwargs):
        super(ConfigurationForm, self).__init__(*args, **kwargs)

#----------- Login ---------------------
class LoginForm(Form):
    username = TextField('Username', [Length(min=4, max=25)])
    password = PasswordField('New Password', [
        Required(),
    ])
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
