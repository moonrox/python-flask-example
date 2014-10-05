### Status will have one of these values
###   null     = new values entered but not acted on
###   dsabled = monitoring has been shut off 
###   enabled  = window reached its maximum value
###   reset    = end a previously scheduled window early

#import sqlite3, datetime, time
import time
from datetime import datetime, timedelta
import MySQLdb as mdb
#import SEC_send, BEM_send
import BEM_send
import sys
import pdb

def send2BEM(hostnm, monitor, action):
	# disable request
	# enable request
	good = BEM_send.msend(hostnm, monitor, "", action)
	return

def send2SEC(hostnm, monitor, action):
	# disable request
	# enable request
	good = SEC_send.publish(hostnm, monitor, action)
	return good

def send2SCOM():
	# disable request
	# enable request
	return

class setRow(object):
	def __init__(self, system_name, monitor_name, req_type, project_name):
		self.name = system_name
		self.monitor = monitor_name
        	self.req_type = req_type
		self.project = project_name

def logerr(errstring, errtype):
    x = open("./process_status.error.txt", "a")
    error = str(errstring) + ":" + str(errtype)
    x.write(error)
     
def delete_sys_state(servername):
    try:
         print "inside delete_sys_state"
         db = mdb.connect('10.65.25.32', 'disablemonitors','d!sablem3','disabletracker');
         utctime = datetime.now()
         starttime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
         cursor = db.cursor()
         sql = """delete from sys_state where name = '"""+servername+"""';"""
         print "sql statement inside delete_sys_state: " + sql
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

while True:
    try:
       conn = mdb.connect('10.65.25.32', 'disablemonitors','d!sablem3','disabletracker')
    except:
	    logerr("for system in startupd", sys.exc_info()[0])

    utctime = datetime.utcnow()
    utcstr = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    d = conn.cursor()
    #### find items that should be re-enabled due to time elapsing
    stopupd=[]
    #d.execute("select * from sys_state where status = 'DISABLED'; ")
    sql = """select name from sys_state where stop < '"""+utcstr+"""';"""
    d.execute(sql)
    #stoprows = d.fetchall()
    server_name = d.fetchone()
    print "server_name1: " + str(server_name)
    servername = str(server_name).replace(',','')
    print "server_name2: " + servername
    servername = servername.replace(')','')
    servername = servername.replace('(','')
    servername = servername[1:-1]
    print "servername: " + servername
    print "utcstr: " + utcstr
    if servername != "on":
        #sentBEM = send2BEM(servername, "all", "admin.remove_host")
        sentBEM = BEM_send.msend(servername, "all","test","APP_ARIES_L1", "Admin_Event: remove_host_from_suppress_table", "admin.remove_host")
        print "sentBEM: " + str(sentBEM)
        print "next step is delete_sys_state"
        send_delete_sys_state = delete_sys_state(servername)
        print send_delete_sys_state

    '''
    try:
        d = conn.cursor()
        #### find items that should be re-enabled due to time elapsing
        stopupd=[]
        #d.execute("select * from sys_state where status = 'DISABLED'; ")
        sql = """select name from sys_state where stop < '"""+utcstr+"""';"""
        d.execute(sql)
        #stoprows = d.fetchall()
        server_name = d.fetchone()
        print "server_name1: " + str(server_name)
        servername = str(server_name).replace(',','')
        print "server_name2: " + servername
        servername = servername.replace(')','')
        servername = servername.replace('(','')
        servername = servername[1:-1]
        print "servername: " + servername
        print "utcstr: " + utcstr
        print "crap"
        #sentBEM = send2BEM(servername, "all", "admin.remove_host")
        sentBEM = BEM_send.msend(servername, "all", "Admin_Event: remove_host_from_suppress_table", "admin.remove_host")
        print "sentBEM: " + sentBEM
        print "next step is delete_sys_state"
        send_delete_sys_state = delete_sys_state(servername)
        print send_delete_sys_state

    except:
        logerr("for system in startupd", sys.exc_info()[0])
    '''

    e = conn.cursor()
    ### update new arrivals
    try:
        for system in startupd:
            ### save the current row
            e.execute("update sys_state set status = 'DISABLED' where location = '%s' and name = '%s' and project = '%s';" % (system.name, system.monitor, system.project) )	
	    e.execute("insert into history (type, name, location, start, stop, comment, status, requester, project, collection) \
			select * from sys_state where location = '%s' and name = '%s' and project = '%s' ;"  \
			% (system.name, system.monitor, system.project) )
    except:
	    logerr("for system in startupd", sys.exc_info()[0])

    try:
        ### update those that exceeded their stop value
        for system in stopupd:
            e.execute("update sys_state set status = 'ENABLED' where location = '%s' and status = 'DISABLED' and name = '%s' and project = '%s' ;" % (system.name, system.monitor, system.project) )
	    e.execute("insert into history (type, name, location, start, stop, comment, status, requester, project, collection) \
			select * from sys_state where location = '%s' and name = '%s' and project = '%s' ;"  \
			% (system.name, system.monitor, system.project) )
    except:
	    logerr("for system in startupd", sys.exc_info()[0])

    try:
        ### process interruptions to an existing window
        for system in resetupd:
            e.execute("update sys_state set status = 'ENABLED', stop = '%s' where location = '%s' and status = 'RESET' and name = '%s' and project = '%s' ;" % (utcstr,system.name, system.monitor, system.project) )
	    e.execute("insert into history (type, name, location, start, stop, comment, status, requester, project, collection) \
			select * from sys_state where location = '%s' and name = '%s' and project = '%s' ;"  \
			% (system.name, system.monitor, system.project) )
    except:
	    logerr("for system in startupd", sys.exc_info()[0])

    conn.commit()
    conn.close()
    time.sleep(30)

