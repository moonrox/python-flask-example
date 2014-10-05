import argparse, urllib2, base64, sys, json, getpass
import base64, json, getpass, httplib

def enable_members(host, port, method, path, headers, args, pool_id, members_ids):
    connection = httplib.HTTPSConnection(host) if port == 443 else httplib.HTTPConnection(host, port)
    data = {
        "environments":[{
            "id": args.envid,
            "pools":[{
                "id": pool_id,
                "members": []
            }]
        }]
    }
    for member_id in members_ids:
        data["environments"][0]["pools"][0]["members"].append({"id":member_id, "state":"enable"})
    print "Enabling members with data:", data
    connection.request(method, path, json.dumps(data), headers)
    return json.loads(connection.getresponse().read())

def disable_members(host, port, method, path, headers, args, pool_id, members_ids):
    connection = httplib.HTTPSConnection(host) if port == 443 else httplib.HTTPConnection(host, port)
    data = {
        "environments":[{
            "id": args.envid,
            "pools":[{
                "id": pool_id,
                "members": []
            }]
        }]
    }
    for member_id in members_ids:
        data["environments"][0]["pools"][0]["members"].append({"id":member_id, "state":"force-offline"})
    print "Disabling members with data:", data
    connection.request(method, path, json.dumps(data), headers)
    return json.loads(connection.getresponse().read())

def delete_member(host, port, method, path, headers):
    connection = httplib.HTTPSConnection(host) if port == 443 else httplib.HTTPConnection(host, port)
    print "Deleting Member:", path
    connection.request(method, path, headers=headers)
    connection.getresponse()

def members(envid,pool_value,memberid1,memberid2,memberid3,credentials):
    data = json.dumps({"environments":[{"id":envid, "pools":[{"id":pool_value,"members":[{"id":memberid1, "state":"enable"},{"id":memberid2, "state":"enable"},{"id":memberid3, "state":"enable"}]}]}]})
    host = 'lbssdev.cps.intel.com'
    path = '/api/environments/pools/members/'
    headers = {'Content-type': 'application/json', "Authorization": "Basic %s" % credentials}

    connection =  httplib.HTTPSConnection(host)
    connection.request('PUT', path, data, headers)
    return json.loads(connection.getresponse().read())

