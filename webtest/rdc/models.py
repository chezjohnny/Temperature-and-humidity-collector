#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask
from sqlalchemy import and_, desc
from flaskext.sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class DataSensors(db.Model):
    __tablename__ = 'rdc_collected_data'
    id = db.Column(db.Integer, primary_key=True)
    date_statement =  db.Column(db.DateTime())
    sensor_value =  db.Column(db.String(50))
    sensor_type =  db.Column(db.String(50))
    collector_id = db.Column(db.Integer, db.ForeignKey('rdc_data_collector.id'))
    def __init__(self, date_statement, sensor_value, sensor_type):
        self.date_statement = date_statement
        self.sensor_value = sensor_value
        self.sensor_type = sensor_type
    def __repr__(self):
        return "<DataSensors('%s','%s', '%s', '%s')>" % (self.date_statement,
                self.sensor_value, self.sensor_type, self.collector_id)

class DataCollector(db.Model):
    __tablename__ = 'rdc_data_collector'
    id = db.Column(db.Integer, primary_key=True)
    host_name =  db.Column(db.String(50))
    state =  db.Column(db.String(50))
    alert_warning_value = db.Column(db.Float)
    alert_critical_value = db.Column(db.Float)
    notifiers =  db.Column(db.String(128))
    data = db.relationship('DataSensors', backref='collector',
                                            lazy='dynamic')
    def __init__(self, host_name, state, alert_warning_value,
            alert_critical_value, notifiers):
        self.host_name =  host_name
        self.state = state
        self.alert_warning_value = alert_warning_value
        self.alert_critical_value = alert_critical_value
        self.notifiers = notifiers

    def __repr__(self):
        return "<DataCollector('%s','%s', '%s', '%s'))>" % (self.host_name,
                self.state, self.alert_warning_value,
                self.alert_critical_value)

    def get_data(self, from_date, to_date, sensor_type="TEMPERATURE",
            max_n_points=None, isoformat=False):
        data = DataSensors.query.filter(and_(DataSensors.collector_id==self.id,
            DataSensors.sensor_type==sensor_type)).filter(and_(DataSensors.date_statement
                <= to_date, DataSensors.date_statement >= from_date,
                DataSensors.sensor_value !=
                'NULL')).order_by(DataSensors.date_statement).all()
        values = []
        one_over_n = 0
        if max_n_points:
            one_over_n = (len(data) / max_n_points) - 1
        n = 0
        for d in data:
            if n >= one_over_n:
                date = d.date_statement
                if isoformat:
                    date = int(float(d.date_statement.strftime('%s'))*1000)
                value = d.sensor_value
                if sensor_type == "TEMPERATURE":
                    value = float(value)
                values.append([date, value])
                n = 0
            else:
                n +=1
        return values

    def last_value(self, sensor_type='TEMPERATURE'):
        last_value = DataSensors.query.filter(and_(DataSensors.collector_id==self.id,
            DataSensors.sensor_type==sensor_type)).order_by(desc(DataSensors.date_statement)).limit(1).first()
        if last_value:
            return (last_value.date_statement, last_value.sensor_value)
        return None
    def get_info(self):
        class Info(object):
            pass
        last_temp = self.last_value()
        info = Info()
        info.date = last_temp[0].strftime('%d %h %Y')
        info.time = last_temp[0].strftime('%H:%M:%S')
        info.temperature = "%.2f" % float(last_temp[1])
        info.name = self.host_name
        info.state = self.state.lower()
        info.balance = self.last_value('BALANCE')[1]
        info.expiration = self.last_value('EXPIRATION')[1]
        info.id = self.id
        return info
