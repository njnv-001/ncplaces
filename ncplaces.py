#!/usr/local/bin/python
from bs4 import BeautifulSoup
import urllib2
import re
import json
import time
import sys

def finditem (element, itemname):
	items = list()
	itemregex = '.*>' + itemname + '<.*'
	m = re.search(itemregex, str(element.contents))
	if m is not None:
		for li in element.findNext('ul').findAll('li'):
			if li.string is None:
				a = li.findNext('a')
				items.append(a.string)
			else:
				items.append(li.string)
	return items

def finddivision(element, names):
	founditems = list()
	for name in names:
		founditems = finditem(element, name)
		if len(founditems) > 0:
			return founditems

def ary2childnodes(nodename, ary):
	parent = dict()
	parent['name'] = nodename
	nodes = list()
	for a in ary:
		node = dict()
		node['name'] = a
		nodes.append(node)
	if len(ary) > 0:
		parent['children'] = nodes
	return parent 

def by_county(countyname):
	urlcounty = 'http://en.wikipedia.org/wiki/' +\
		countyname.replace(' ', '_') + \
		',_North_Carolina'
	#f = urllib2.urlopen("http://en.wikipedia.org/wiki/Alamance_County,_North_Carolina")
	f = urllib2.urlopen(urlcounty)
	# Alexander County doesn't use the same page format as other NC county
	# Wikipedia pages - will need to pass in bs4 search functions
	# as parameters
	#f = urllib2.urlopen("http://en.wikipedia.org/wiki/Alexander_County,_North_Carolina")
	soup = BeautifulSoup(f)
	cities = list()
	towns = list()
	villages = list()
	townships = list()
	csds = list()
	uics = list()
	for h3 in soup.findAll('h3'):
		foundcities = finddivision(h3, ['City', 'Cities'])
		if foundcities is not None:
			cities = foundcities
	
		foundtowns = finddivision(h3, ['Town', 'Towns'])
		if foundtowns is not None:
			towns = foundtowns
	
		foundvillages = finddivision(h3, ['Village', 'Villages'])
		if foundvillages is not None:
			villages = foundvillages
	
		foundtownships = finddivision(h3, ['Township', 'Townships'])
		if foundtownships is not None:
			townships = foundtownships
	
		foundcsds = finddivision(h3, ['Census-designated place', 'Census-designated places'])
		if foundcsds is not None:
			csds = foundcsds
	
		founduics = finddivision(h3, ['Unincorporated community', 'Unincorporated communities'])
		if founduics is not None:
			uics = founduics
	
	countylist = list()
	countylist.append(ary2childnodes('Cities', cities))
	countylist.append(ary2childnodes('Towns', towns))
	countylist.append(ary2childnodes('Villages', villages))
	countylist.append(ary2childnodes('Townships', townships))
	countylist.append(ary2childnodes('Census-designated places', csds))
	countylist.append(ary2childnodes('Unincorporated communities', uics))
	countydict = dict()
	countydict['name'] = countyname
	countydict['children'] = countylist
	return countydict

f = urllib2.urlopen("http://en.wikipedia.org/wiki/List_of_counties_in_North_Carolina")
soup = BeautifulSoup(f)
counties = dict()
for tr in soup.findAll('tr'):
	cellone = tr.findNext('td');
	countyregex = 'County'
	if cellone.string is not None:
		c = re.search(countyregex, cellone.string)
		if c is not None:
			counties[cellone.string] = cellone.string

# A-F
# G-M
# N-R
# S-Z
ctyaf = list()
ctygm = list()
ctynr = list()
ctysz = list()
for county in sorted(counties):
	firstletter = county[0]
	print firstletter
	sys.stdout.flush()
	countydivs = by_county(county)
	if firstletter < 'G':
		ctyaf.append(countydivs)
	elif firstletter < 'N':
		ctygm.append(countydivs)
	elif firstletter < 'S':
		ctynr.append(countydivs)
	else:
		ctysz.append(countydivs)
#	time.sleep(2)

ctyafnode = dict()
ctyafnode['name'] = 'Counties A-F'
ctyafnode['children'] = ctyaf

ctygmnode = dict()
ctygmnode['name'] = 'Counties G-M'
ctygmnode['children'] = ctygm

ctynrnode = dict()
ctynrnode['name'] = 'Counties N-R'
ctynrnode['children'] = ctynr

ctysznode = dict()
ctysznode['name'] = 'Counties S-Z'
ctysznode['children'] = ctysz

state = dict()
state['name'] = 'North Carolina'
state['children'] = [ctyafnode, ctygmnode, ctynrnode, ctysznode]
print json.dumps(state)


