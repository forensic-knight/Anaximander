#!/usr/bin/python
# Python:        2.7
# Filename:      Anaximander_54.py
# Purpose:       Enrich UFED XML Report files with celltower geo data
# Authors:       Matt Edmondson
#                Thanks to Ed Michael & Douglas Kein
# Modified by:   Forensic Knight :)
# Version:       0.9 2017-02-20
# Bug-Reports:   see https://github.com/forensic-knight/Anaximander and https://github.com/azmatt/Anaximander
# License:       This file is licensed under the GPL v3.
################################################################################

import xml.etree.ElementTree as ET
import sqlite3
import os
import optparse
import sys

####Forces input of xml file
parser = optparse.OptionParser('correct usage is: Anaximander.py -t' + ' CellebriteTowers.xml')
parser.add_option('-t', dest='targetpage', type='string', help='Specify the Cellebrite cellphone tower XML output file')
(options, args) = parser.parse_args()
tgtFile = options.targetpage
if (tgtFile == None):
	print parser.usage
	sys.exit(0)

z = open('cellTowers.kml', 'w')
z.write("<?xml version='1.0' encoding='UTF-8'?>\n")
z.write("<kml xmlns='http://earth.google.com/kml/2.1' xmlns:gx='http://www.google.com/kml/ext/2.2'>n" )
z.write("<Document>\n")
z.write("   <name> Cell Towers </name>\n")

tree = ET.parse(tgtFile)
root = tree.getroot()
x = 0
for child in root[6][0]:
        print "############################"
	varTimestamp = root[6][0][x][2][0].text
	#print "Timestamp: %s" % varTimestamp
	varPackageType = root[6][0][x][3][0].text
	#print "Package Type: %s " % varPackageType
	varCellTowerType = root[6][0][x][4][0].text
	#print "Cell Tower Type: %s" % varCellTowerType
	varMcc = root[6][0][x][5][0].text
	#print "MCC: %s" % varMcc
	varMnc = root[6][0][x][6][0].text
	#print "MNC: %s " % varMnc
        # UFED delivers some MNCs with leading zeros!
        if varMnc[0] == '0':
           print "[i] Removed leading zero of current MNC!"
           varMnc = varMnc.lstrip('0');
	varLac = root[6][0][x][7][0].text
	#print "LAC: %s" % varLac
	varCid = root[6][0][x][8][0].text
	#print "CID: %s" % varCid
	print "[+] Inserting the following record (MCC: %s, MNC: %s, LAC: %s, CID: %s)" % (varMcc, varMnc, varLac, varCid)
	print "[+] Cont: (Timestamp: %s, Pack Type: %s, Cell Tower Type: %s)" % (varTimestamp, varPackageType, varCellTowerType)
	
	###DB for Tower Locations
	db = sqlite3.connect('cellTowers.sqlite')
	cursor = db.cursor()
	cursor.execute("select * from towers where mcc = '%s' and net = '%s' and area = '%s' and cell = '%s' limit 1" % (varMcc, varMnc, varLac, varCid) )
        r = 0
	for row in cursor:
                r += 1
		try:
			varLon = row[6]
			#print "Lon: %s" % varLon
			varLat = row[7]
			#print "Lat: %s " % varLat
			print "[+] Enrich: (Lon: %s, Lat: %s)" % (varLon, varLat)
			
			
			kml_contents = " <Placemark>\n <TimeStamp><when>"+ varTimestamp +"</when></TimeStamp> <name>" + str(x)+ "</name>\n <description> <p><b>Cell ID:</b> " + varCid + "</p><p><b>Date:</b> " + varTimestamp + "</p></description>\n <Point>\n <coordinates>" + varLon + "," + varLat + ",0 </coordinates>\n </Point>\n </Placemark>\n"
			z.write(kml_contents)
		except:
			print "[!] Error with the following record (MCC: %s, MNC: %s, LAC: %s, CID: %s)!" % (varMcc, varMnc, varLac, varCid)
        if r == 0:
           print "[!] Error: No matching record found!"
	x =x + 1
	
cursor.close
print
print "############################ Summary ############################"
print "\n%s Records Parsed" % x

######Finalizing and Closing KML############
z.write("</Document>\n")
z.write("</kml>\n")
z.close()
print"[+] Generated KML file"