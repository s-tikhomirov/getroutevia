#!/usr/bin/env python3
from pyln.client import Plugin, RpcError
import random
from collections import deque 

plugin = Plugin()

def route_includes_all_of(route, nodes_to_include):
	nodes = [hop["id"] for hop in route]
	route_ok = all([n in nodes for n in nodes_to_include])
	return route_ok

def route_includes_any_of(route, nodes_to_include):
	nodes = [hop["id"] for hop in route]
	route_ok = any([n in nodes for n in nodes_to_include])
	return route_ok

# Just a silly criteria exemplifying what may be plugged in as route_ok function
def all_nodeids_even(route):
	nodes = [hop["id"] for hop in route]
	route_ok = all([n[-1] not in ["2","4","8"] for n in nodes])
	return route_ok


'''
	Determine if the route is OK w.r.t. some condition
'''
def route_ok(route, nodes_to_include):
	return route_includes_any_of(route, nodes_to_include)


'''
	getroutevia calls getroute with some channels excluded until the condition is met
	The list of included channels is updates in a BFS-like fashion.
	Usage: same as getroute with additional parameters:
	include_node: the route must go through this node
	max_attempts: the maximum number of tries
'''
@plugin.method("getroutevia")
def getroutevia(plugin, id, msatoshi, riskfactor,
	include_node=None,
	cltv=9, fromid=None, fuzzpercent=5, exclude=[], maxhops=20,
	max_attempts=10000):
	if fromid == None:
		fromid = plugin.rpc.getinfo()["id"]
	route = None
	num_attempts = 0
	include_nodes = [include_node] if include_node else []
	excluded_channels_lists = deque()
	# exclude contains (channel id / direction)s and node ids initially marked for exclusion
	excluded_channels_lists.append(exclude)
	while excluded_channels_lists and num_attempts < max_attempts:
		num_attempts += 1
		excluded_channels = excluded_channels_lists.popleft()
		#print("Attempt", num_attempts, ", finding route with excluded channels:", excluded_channels)
		try:
			candidate_route = plugin.rpc.getroute(id, msatoshi, riskfactor, 
				cltv, fromid, fuzzpercent, excluded_channels, maxhops)["route"]
			if route_ok(candidate_route, include_nodes):
				route = candidate_route
				break
			else:
				channels = [hop["channel"] + "/" + str(hop["direction"]) for hop in candidate_route]
				random.shuffle(channels)
				for channel in channels:
					#print("Adding", channel, "to exclude, got", excluded_channels_1)
					excluded_channels_lists.append(excluded_channels + [channel])
		except RpcError:
			pass
	if route:
		print("Found route of length", len(route), "after", num_attempts, "attempts.")
	else:
		print("No route found after", num_attempts, "attempts.")
	return route


@plugin.init()
def init(options, configuration, plugin):
    plugin.log("Plugin getroutevia.py initialized")

plugin.run()