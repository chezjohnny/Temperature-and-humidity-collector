#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flaskext.wtf import Form, BooleanField, TextField, PasswordField, validators, DecimalField

#----------- Registration ---------------------
class ConfigurationForm(Form):

    enabled = BooleanField('Actif')
    alert_warning_value = DecimalField('Alerte',
            [validators.NumberRange(min=-10, max=10, message="La valeur doit etre entre -10 et 10")])
    alert_critical_value = DecimalField('Alerte Critique',
            [validators.NumberRange(min=-10, max=10, message="La valeur doit etre entre -10 et 10")])
    notifiers = TextField('Notifications')
    def __init__(self, *args, **kwargs):
        super(ConfigurationForm, self).__init__(*args, **kwargs)

#----------- Login ---------------------
class LoginForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('New Password', [
        validators.Required(),
    ])
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
