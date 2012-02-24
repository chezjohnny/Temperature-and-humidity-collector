#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Blueprint, g

from ..tools import templated, get_best_language, get_user
from flask import render_template, request, flash, redirect, url_for, session, g, abort, current_app, jsonify
from flaskext.login import login_user, login_required, logout_user, AnonymousUser
import hashlib
from ..models import DataCollector
from .. import forms
import datetime

mobile = Blueprint('mobile', __name__, url_prefix='/mobile',
        template_folder='templates', static_folder='static')


#---------- Routes ------------
@mobile.route("/login", methods=["GET", "POST"])
@templated()
def login():
    print "Login"
    form = forms.LoginForm(csrf_enabled=False)
    print request.method, form.validate_on_submit()
    if request.method == 'POST' and form.validate_on_submit():
        # login and validate the user...
        user = get_user(form.username.data, form.password.data)
        print user
        if user is None:
            flash("Bad username or password.", "error")
            return dict(form=form)
        login_user(user)
        flash("Logged in successfully.", "info")
        return redirect(url_for("mobile.configuration"))
    return dict(form=form)

@mobile.route('/logout')
def logout():
    flash('You were logged out', "warning")
    logout_user()
    return redirect(request.args.get("next") or url_for('mobile.index'))

@mobile.route('/configuration', methods=["GET", "POST"])
@login_required
@templated("mobile/index.html")
def configuration():
    return dict(title="Configuration", page_id="conf-page", msg="Config")

@mobile.route('/data/', defaults={'host_id':
'1', 'sensor_type':'TEMPERATURE', 'period':'day'})
@mobile.route('/data/<host_id>/', defaults={'sensor_type':'TEMPERATURE', 'period':'day'})
@mobile.route('/data/<host_id>/<sensor_type>/',defaults={'period':'day'})
@mobile.route('/data/<host_id>/<sensor_type>/<period>')
def get_temperature_data(host_id, sensor_type, period):
    dc = DataCollector.query.filter(DataCollector.id == host_id).first()
    now = datetime.datetime.now()
    to_date = now
    if period == 'month':
        from_date = now - datetime.timedelta(days=30)
    elif period == 'week':
        from_date = now - datetime.timedelta(days=7)
        print "week"
    else:
        from_date = now - datetime.timedelta(days=1)
    data = dc.get_data(from_date, to_date, sensor_type, 400, True)
    return jsonify({'data': data, 'warning': dc.alert_warning_value,
        'critical': dc.alert_critical_value, 'host_name' : dc.host_name})



@mobile.route('/plot/<int:host_id>')
@templated()
def plot(host_id):
    dc = DataCollector.query.filter(DataCollector.id == host_id).first()
    return dict(page_id='dataPage', host_id=host_id, host_name=dc.host_name)

@mobile.route('/')
@templated()
def index():
    infos = []
    for dc in DataCollector.query.all():
        infos.append(dc.get_info())

    return dict(title="mobile", page_id="main-page", host_informations=infos)

@mobile.route('/admin')
@templated('mobile/index.html')
@login_required
def admin():
    return dict(title="Admin area", msg="You are on a protected page!")


#@mobile.route('/lang/<lang>')
#def set_language(lang):
#    if lang in ['en', 'fr']:
#        session['lang'] = lang
#    return redirect(request.args.get("next") or url_for('index'))


#@app.route('/register', methods=['GET', 'POST'])
#@templated()
#def register():
#    form = forms.RegistrationForm(request.form)
#    if request.method == 'POST' and form.validate():
#        flash('Thanks for registering', 'info')
#        return redirect(url_for('login'))
#    return dict(form=form)


@mobile.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404