import argparse, base64, getpass
import create_vip
import create_pool
import enable_pool
import time

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--username", help="Username")
parser.add_argument("-w", "--password", help="Password")
parser.add_argument("-e", "--envid", help="Environment ID")
parser.add_argument("-g", "--groupid", help="Group ID number")
parser.add_argument("-n", "--poolname", help="Pool name")
parser.add_argument("-l", "--lbmethod", help="Load Balancing method")
parser.add_argument("-o", "--monitor", help="Monitor name.  ex: DBaaS_mongo.")
parser.add_argument("-a", "--priority_activation", help="Priority group activation. True or False.")
parser.add_argument("-c", "--priority_connections", help="Least connection members.")
parser.add_argument("-r", "--priority_groups", help="List of priority groups, same length of members list.")
parser.add_argument("-m", "--members", help="List of members, comma separated, no spaces, format IP:PORT")
parser.add_argument("-v", "--vipname", help="VIP Name" )
parser.add_argument("-t", "--iptype", help="IP Type. private or public")
parser.add_argument("-p", "--vipport", help="VIP port" )
args = parser.parse_args()

def validate_params(args):
	errors = []
	if not args.password:
		args.password = getpass.getpass("Password: ")
	if not args.username:
		errors.append("Username is required")
	elif "\\" in args.username:
		errors.append("Username does not need Domain")
	if args.envid and args.envid.isdigit():
		args.envid = int(args.envid)
	else:
		errors.append("Enter a valid Environment ID")
	if args.groupid and args.groupid.isdigit():
		args.groupid = int(args.groupid)
	else:
		errors.append("Enter a valid Group ID")
	if not args.poolname:
		errors.append("Enter a pool name")
	if not args.lbmethod:
		errors.append("Enter a load balancing method")
	args.priority_activation = True if args.priority_activation == "True" else False
	args.priority_connections = int(args.priority_connections) if args.priority_connections and args.priority_connections.isdigit() else 0
	priority_groups = []
	if args.priority_groups:
		for priority_group in args.priority_groups.split(","):
			if priority_group.isdigit():
				priority_groups.append(int(priority_group))
			else:
				errors.append("Priority group: "+priority_group+" is not valid")
	args.priority_groups = priority_groups
	members = []
	if args.members:
		for member in args.members.split(","):
			if len(member.split(":")) == 2:
				members.append(member)
			else:
				errors.append("Member: "+member+" is not valid")
	args.members = members
	if len(members) != len(priority_groups) and args.priority_activation:
		errors.append("Members list and priority groups list are not equal")
	if not args.vipname:
		errors.append("Enter a VIP name")
	if not (args.iptype == "private" or args.iptype == "public"):
		errors.append("IP type should be 'public' or 'private'")
	if args.vipport and args.vipport.isdigit():
		args.vipport = int(args.vipport)
	else:
		errors.append("Enter a valid VIP port")
	print "username: ", args.username
	print "envid: ", args.envid
	print "groupid: ", args.groupid
	print "poolname: ", args.poolname
	print "lbmethod: ", args.lbmethod
	print "monitor: ", args.monitor
	print "priority_activation: ", args.priority_activation
	print "priority_connections: ", args.priority_connections
	print "priority_groups: ", args.priority_groups
	print "members: ", args.members
	print "vipname: ", args.vipname
	print "iptype: ", args.iptype
	print "vipport: ", args.vipport

	if errors:
		print "\nErrors:"
		for error in errors:
			print error
		exit(1)

validate_params(args)

host = 'lbssdev.cps.intel.com'
port = 443
#host = '127.0.0.1'
#port = 8000
credentials = base64.encodestring(u"amr\\"+args.username+":"+args.password).strip()
headers = {'Content-type': 'application/json', "Authorization": "Basic %s" % credentials}
rollback = True

pool_value = create_pool.create_pool(host, port, 'POST', '/api/environments/pools/', headers, args)
print "\nResponse:", pool_value, "\n"
if pool_value['status']:
	pool_id = pool_value['environments'][0]['pools'][0]['id']
	members_ids = []
	for member in pool_value['environments'][0]['pools'][0]['members']:
		members_ids.append(member['id'])
	print "Pool ID: ", pool_id
	for member_id in members_ids:
		print "Member ID: ", member_id

	if pool_id:
		vip_value = create_vip.create_vip(host, port, 'POST', '/api/environments/vips/', headers, args, pool_id)
		print "\nResponse:", vip_value, "\n"

	if members_ids:
		member_value = enable_pool.enable_members(host, port, 'PUT', '/api/environments/pools/members/', headers, args, pool_id, members_ids)
		print "\nResponse:", member_value, "\n"

	if rollback:
		print "Rolling back ..."
                time.sleep(30)
		if vip_value['status']:
			vip_id = vip_value['environments'][0]['virtuals'][0]['id']
			create_vip.delete_vip(host, port, 'DELETE', '/api/environments/'+str(args.envid)+'/vips/'+str(vip_id)+"/", headers)

		if members_ids and member_value['status']:
			enable_pool.disable_members(host, port, 'PUT', '/api/environments/pools/members/', headers, args, pool_id, members_ids)	
			for member_id in members_ids:
				enable_pool.delete_member(host, port, 'DELETE', '/api/environments/'+str(args.envid)+'/pools/'+str(pool_id)+'/members/'+str(member_id)+'/', headers)

		create_pool.delete_pool(host, port, 'DELETE', '/api/environments/'+str(args.envid)+'/pools/'+str(pool_id)+'/', headers)

