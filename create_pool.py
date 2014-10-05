import urllib2, json, httplib

def create_pool(host, port, method, path, headers, args):
    connection = httplib.HTTPSConnection(host) if port == 443 else httplib.HTTPConnection(host, port)
    data = {
        "environments":[{
            "id": args.envid,
            "pools":[{
                "name": args.poolname,
                "lb_method": args.lbmethod,
                "monitors": [args.monitor],
            }]
        }],
        "user_group":{
            "id": args.groupid
        }
    }
    if args.priority_activation:
        data['environments'][0]['pools'][0]['priority_groups_activation'] = True
        data['environments'][0]['pools'][0]['least_active_members'] = args.priority_connections
    members_list = []
    for member_index in range(len(args.members)):
        member = {
            "address": args.members[member_index].split(":")[0],
            "port": args.members[member_index].split(":")[1],
            }
        if args.priority_activation:
            member["priority_group"] = args.priority_groups[member_index]
        members_list.append(member)
    if members_list:
        data['environments'][0]['pools'][0]['members'] = members_list
    print "Creating Pool with data:", data
    connection.request(method, path, json.dumps(data), headers)
    return json.loads(connection.getresponse().read())

def delete_pool(host, port, method, path, headers):
    connection = httplib.HTTPSConnection(host) if port == 443 else httplib.HTTPConnection(host, port)
    print "Deleting Pool:", path
    connection.request(method, path, headers=headers)
    connection.getresponse()

def pool(envid,port,lbmethod,groupid,credentials,poolname,vm1,vm2,vm3,monitor,numofmembers):
    url = 'https://lbssdev.cps.intel.com/api/environments/pools/'
    headers = {'Content-type': 'application/json', "Authorization": "Basic %s" % credentials}
    post_data = ""

    if numofmembers == '3':
        post_data = json.dumps({"environments":[{"id":envid,"pools":[{"name":poolname, "lb_method":lbmethod,"least_active_members":"1","priority_groups_activation":True, "monitors":[monitor], "members":[{"address":vm1, "port":port,"priority_group":"10"},{"address":vm2, "port":port, "priority_group":"5"},{"address":vm3, "port":port, "priority_group":"1"}]}]}], "user_group":{"id":groupid}})

    if numofmembers == '2':
        post_data = json.dumps({"environments":[{"id":args.envid,"pools":[{"name":args.poolname, "lb_method":args.lbmethod,"least_active_members":"1","priority_groups_activation":"True","monitors":[args.monitor], "members":[{"address":args.vm1, "port":args.port,"priority_group":"10"},{"address":args.vm2, "port":args.port,"priority_group":"5"}]}]}], "user_group":{"id":args.groupid}})

    if numofmembers == '1':
        post_data = json.dumps({"environments":[{"id":args.envid,"pools":[{"name":args.poolname, "lb_method":args.lbmethod,"least_active_members":"1","priority_groups_activation":"True","monitors":[args.monitor], "members":[{"address":args.vm1, "port":args.port,"priority_group":"10"}]}]}], "user_group":{"id":args.groupid}})

    request = urllib2.Request(url, post_data, headers=headers)
    response = urllib2.urlopen(request).read()
    return json.loads(response)




