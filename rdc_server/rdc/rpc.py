from flaskext.xmlrpc import XMLRPCHandler, Fault
rpc_handler = XMLRPCHandler('api')
from models import DataSensors, DataCollector, db
import datetime

@rpc_handler.register
def add_data(host_name, date_statement, sensor_value, sensor_type="TEMPERATURE"):
    date_statement = datetime.datetime.strptime(date_statement, '%Y-%m-%dT%H:%M:%S.%f')
    dc = DataCollector.query.filter(DataCollector.host_name == host_name).first()
    if not dc:
        dc = DataCollector(host_name, "DISABLE", "-10", "-20","")
    s = DataSensors(date_statement, sensor_value, sensor_type)
    dc.data.append(s)
    db.session.merge(dc)
    db.session.merge(s)
    db.session.commit()

        #raise Fault("Mon exception", "I need someone to greeti %s!" %
        #        (type(Fault)))
    return "Data added in %s!" % dc.host_name

@rpc_handler.register
def get_data(host_name):
    dc = DataCollector.query.filter(DataCollector.host_name == host_name).first()

    if not dc:
        raise Fault("HostNameError", "Host name %s does not exists in database!" %
                host_name)
    return "%s data in %s!" % (len(dc.data.all()), dc.host_name)
