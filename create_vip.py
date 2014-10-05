import urllib2, json, httplib

def create_vip(host, port, method, path, headers, args, pool_id):
    connection = httplib.HTTPSConnection(host) if port == 443 else httplib.HTTPConnection(host, port)
    data = {
        "environments":[{
            "id": args.envid,
            "virtuals":[{
                "name": args.vipname,
                "ip_type": args.iptype,
                "port": args.vipport,
                "pool":{
                    "id": pool_id
                }
            }]
        }],
        "user_group":{
            "id": args.groupid
        }
    }
    print "Creating VIP with data:", data
    connection.request(method, path, json.dumps(data), headers)
    return json.loads(connection.getresponse().read())

def delete_vip(host, port, method, path, headers):
    connection = httplib.HTTPSConnection(host) if port == 443 else httplib.HTTPConnection(host, port)
    print "Deleting VIP:", path
    connection.request(method, path, headers=headers)
    connection.getresponse()

def vip(envid,pool_value,vipname,port,iptype,group,credentials):
    url = 'https://lbssdev.cps.intel.com/api/environments/vips/'
    post_data = json.dumps({"environments":[{"id":envid, "virtuals":[{"name":vipname,"pool":{"id": pool_value},"port":port, "ip_type":iptype}]}], "user_group":{"id":group}})
    request = urllib2.Request(url, post_data, headers={'Content-type': 'application/json'})
    request.add_header("Authorization", "Basic %s" % credentials)
    response = urllib2.urlopen(request).read()
    return json.loads(response)
