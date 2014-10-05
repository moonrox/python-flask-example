#################################
# Flask API with Myslq
#
# By:   
# John Monroe
#################################
import re
import json
from flask import Flask, request
import BEM_send
import MySQLdb as mdb
import sys
import MySQLdb
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['DEBUG'] = True

#PARAMS
#Comment these out to debug. :) 
#requestService.config.debug = 1
#app.debug = True
#port=os.environ["port"]

@app.route('/')
def index():
    return 'MM On.  API to write entries into the BEM host suppression table'

@app.route('/mm_on/<string:server_name>', methods = ['GET'])
def mm_on(server_name):
    '''
    Uses GET to place a BEM suppression entry into the suppression table.
    '''
    # Normalize the collection name from the URL
    server_name = server_name.lower()
    sentBEM = BEM_send.msend(server_name, "all","Admin_Event: add_host_to_suppress_table" , "admin.add_host")
    print sentBEM
    sentlog = log(server_name)
    print sentlog
    return "command submitted"

@app.route('/mm_json', methods = ['POST'])
def mm_json():
    '''
    enables you to post json to the BEM suppression API.
    '''
    server_name = ""
    seconds = ""
    if request.json:
        server_name = request.json["server_name"]
        seconds = request.json["seconds"]
        action = request.json["action"]
        actionprocess = request.json["actionprocess"]
        requester = request.json["requester"]
        bem_class = request.json["bem_class"]
        bca = request.json["bem_class_affected"]
    print "server_name: " + server_name
    print "seconds: " + seconds
    server_name = server_name.lower()
    sentBEM = BEM_send.msend(server_name, "all", seconds, bca, action, actionprocess )
    print sentBEM
    sentlog = log(server_name, seconds, requester, bca)
    send_delete_sys_state = delete_sys_state(server_name, seconds, requester, bca)
    send_create_sys_state = create_sys_state(server_name, seconds, requester, bca)
    print "from mm.py: " + sentlog
    return "command submitted"

def create_sys_state(server_name, seconds, requester, bca):
    try:
        db = mdb.connect('10.65.25.32', 'disablemonitors','d!sablem3','disabletracker');
        utctime = datetime.utcnow()
        utcstr = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        starttime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        value = timedelta(seconds=float(seconds))
        stoptime = utctime + value
        print "starttime: " + starttime
        print "stoptime: " + str(stoptime)
        print "starting the delete check"
        cursor = db.cursor()
        sql = """insert into sys_state (type, name, location, start, stop, comment, status, requester, project, collection) values ('type', '"""+server_name+"""', 'location', '"""+starttime+"""',  '"""+str(stoptime)+"""', ' comment',' status', '"""+requester+"""','"""+bca+"""', 'collection')"""
        print "sql statement: " + sql
        cursor.execute(sql)
        db.commit()
    except mdb.Error, e:
        db.rollback()
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)
    finally:
        if db:
            db.close()

    return "sys_state entry created"

def delete_sys_state(server_name, seconds, requester, bca):
    try:
        db = mdb.connect('10.65.25.32', 'disablemonitors','d!sablem3','disabletracker');
        utctime = datetime.now()
        starttime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        value = timedelta(seconds=float(seconds))
        stoptime = utctime + value
        print "starttime: " + starttime
        print "stoptime: " + str(stoptime)
        print "stoptime: " + str(stoptime)
        print "starting the delete check"
        cursor = db.cursor()
        sql = """delete from sys_state where name = '"""+server_name+"""' and stop < '"""+starttime+"""';"""
        print "sql statement: " + sql
        cursor.execute(sql)
        db.commit()
        
    except mdb.Error, e:
        db.rollback()
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)
    finally:
         if db:
             db.close()
        
    return "if exist sys_state entry deleted"

def log(server_name, seconds, requester, bca):
    try:
        print "seconds from inside log: " + seconds
        db = mdb.connect('10.65.25.32', 'disablemonitors','d!sablem3','disabletracker');
        utctime = datetime.now()
        starttime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        value = timedelta(seconds=float(seconds))
        stoptime = utctime + value
        print "starttime: " + starttime
        print "stoptime: " + str(stoptime)

        cursor = db.cursor()
        sql = """insert into history (type, name, location, start, stop, comment, status, requester, project, collection) values ('type', 'name','"""+server_name+"""', '"""+starttime+"""',  '"""+str(stoptime)+"""', ' comment',' status', '"""+requester+"""','"""+bca+"""', 'collection')"""
        print "sql statement: " + sql
        cursor.execute(sql)
        db.commit()
    except mdb.Error, e:
        db.rollback()
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)

    finally:

        if db:
            db.close()

    return "entry logged"

@app.route('/mm_off/<string:server_name>', methods = ['GET'])
def mm_off(server_name):
    '''
    GET a specific document from a specific shinken_config collection.
    '''
    # Normalize the collection name from the URL
    server_name = server_name.lower()
    sentBEM = BEM_send.msend(server_name, "all", "Admin_Event: remove_host_from_suppress_table", "admin.remove_host")
    print sentBEM
    sentlog = log(server_name)
    print sentlog
    return "command submitted"

if __name__ == '__main__':
    print "MM API started! "
    try:
        #app.run(host='0.0.0.0',port=int(port)) #remove the Host= variable to disable the external connectivity
        app.run(host='0.0.0.0') #remove the Host= variable to disable the external connectivity
    except:
        print("MM API is already running")
