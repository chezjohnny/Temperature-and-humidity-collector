#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask
from rdc import db

class DataSensors(db.Model):
    __tablename__ = 'collected_data'
    id = db.Column(db.Integer, primary_key=True)
    date_statement =  db.Column(db.DateTime())
    sensor_value =  db.Column(db.String(50))
    sensor_type =  db.Column(db.String(50))
    collector_id = db.Column(db.Integer, db.ForeignKey('data_collector.id'))
    def __init__(self, date_statement, sensor_value, sensor_type):
        self.date_statement = date_statement
        self.sensor_value = sensor_value
        self.sensor_type = sensor_type
    def __repr__(self):
        return "<DataSensors('%s','%s', '%s', '%s')>" % (self.date_statement,
                self.sensor_value, self.sensor_type, self.collector_id)

class DataCollector(db.Model):
    __tablename__ = 'data_collector'
    id = db.Column(db.Integer, primary_key=True)
    host_name =  db.Column(db.String(50))
    state =  db.Column(db.String(50))
    last_date_statement =  db.Column(db.DateTime())
    last_sensor_value =  db.Column(db.String(50))
    last_sensor_type =  db.Column(db.String(50))
    alert_warning_value = db.Column(db.Float)
    alert_critical_value = db.Column(db.Float)
    notifiers =  db.Column(db.String(128))
    data = db.relationship('DataSensors', backref='collector',
                                            lazy='dynamic')
    def __init__(self, host_name, state, last_date_statement,
            last_sensor_value, last_sensor_type, alert_warning_value,
            alert_critical_value, notifiers):
        self.host_name =  host_name
        self.state = state
        self.last_date_statement = last_date_statement
        self.last_sensor_value = last_sensor_value
        self.last_sensor_type = last_sensor_type
        self.alert_warning_value = alert_warning_value
        self.alert_critical_value = alert_critical_value
        self.notifiers = notifiers
    def __repr__(self):
        return "<DataCollector('%s','%s', '%s', '%s', '%s','%s', '%s'))>" % (self.host_name,
                self.state, self.last_date_statement, self.last_sensor_value,
                self.last_sensor_type, self.alert_warning_value,
                self.alert_critical_value)
