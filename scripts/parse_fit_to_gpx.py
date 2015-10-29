#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import print_function
import os
import sys
from __builtin__ import isinstance
from math import pow
from datetime import datetime
from os.path import basename


# Add folder to search path

PROJECT_PATH = os.path.realpath(os.path.join(sys.path[0], '..'))
sys.path.append(PROJECT_PATH)

from fitparse import Activity

infos = 'infos' in sys.argv or '-i' in sys.argv
filenames = None

if len(sys.argv) >= 2:
    filenames = [f for f in sys.argv[1:] if os.path.exists(f)]

if not filenames:
    filenames = [os.path.join(PROJECT_PATH, 'tests', 'data', 'sample-activity.fit')]


def print_record(rec, ):
    global record_number
    record_number += 1
    print ("-- %d. #%d: %s (%d entries) " % (record_number, rec.num, rec.type.name, len(rec.fields))).ljust(60, '-')
    for field in rec.fields:
        toprint = "%s [%s]: %s" % (field.name, field.type.name, field.data)
        if field.data is not None and field.units:
            toprint += " [%s]" % field.units
        print(toprint)
    print

#// degrees = semicircles * ( 180 / 2^31 ) see Vasilev program
def semicircle_to_coordinates(semicircles):
    return float(semicircles) * 180 / pow(2, 31)

#transform a datetime into <time>2015-09-26T10:40:29Z</time> see Vasilev output
def datetime_to_gpstimestamps(datetime_object):
    gps_timestamp = ""
    if isinstance(datetime_object, datetime):
        gps_timestamp = datetime_object.strftime("%Y-%m-%dT%H:%M:%SZ")
    return gps_timestamp


#from the Python recipes p 31/252 - 10 
#TODO : add conversion function and formatting function for dates - by default None function cf. base !!!!!!!!     
def retrieve_value_for_display(values, key, converter=None, default=("","%s")):
    found = values.get(key, [''])
    x=default[0]
    f="%s"
    if found:
        x=found
        if x is not None and converter is not None:
            x=converter(x)
        
        if isinstance(x, int):
            found = int(x)
            f="%d"
        elif isinstance(x, float):
            found = float(x)
            f="%d"
        else:
            found = x
            f="%s"
    return (found,f)

def affiche_trkpoinnt(point_gpx):
    if point_gpx is not None:
        print(point_gpx)
    
def return_gpx_trk_entry(rec, ):
    if rec.type.name == "record":
        point_datas={'timestamp':None,'position_long':None,'position_lat':None,'elevation':None,'extras':{'speed':None,'distance':None,'heart_rate':None}}
        for field in rec.fields:
            if field.name == 'timestamp':
                point_datas['timestamp']=field.data
            elif field.name == 'position_lat':
                point_datas['position_lat']=field.data
            elif field.name == 'position_long':
                point_datas['position_long']=field.data
            elif field.name == 'altitude':
                point_datas['altitude']=field.data
            elif field.name == 'speed':
                point_datas['extras']['speed']=field.data
            elif field.name == 'distance':
                point_datas['extras']['distance']=field.data
            elif field.name == 'heart_rate':
                point_datas['extras']['heart_rate']=field.data
        #TODO: use a wrapper / decorator function to give default value wwhen None .... or not printing at all ....
        #make a retrun or yield string instead of a direct print !!!!
        trkpoint_elements_array = []
        trkpoint_elements_array.append("<trkpt lat=\"%s\" lon=\"%s\">" %(retrieve_value_for_display(point_datas,'position_lat',converter=semicircle_to_coordinates)[0],
                                                retrieve_value_for_display(point_datas,'position_long',converter=semicircle_to_coordinates)[0]))
        trkpoint_elements_array.append("<time>%s</time>" %(retrieve_value_for_display(point_datas,"timestamp",converter=datetime_to_gpstimestamps)[0]))
        trkpoint_elements_array.append("<ele>%d</ele>" %(retrieve_value_for_display(point_datas,"altitude")[0]))
        trkpoint_elements_array.append("<extensions>")
        trkpoint_elements_array.append("<nmea:speed>%s</nmea:speed>" %(str(retrieve_value_for_display(point_datas['extras'],'speed')[0])))
        trkpoint_elements_array.append("<gpxtpx:TrackPointExtension>")
        trkpoint_elements_array.append("<gpxtpx:speed>%s</gpxtpx:speed>" %(str(retrieve_value_for_display(point_datas['extras'],'speed')[0])))
        trkpoint_elements_array.append("<gpxtpx:course>%s</gpxtpx:course>" %(str(retrieve_value_for_display(point_datas['extras'],'distance')[0])))
        trkpoint_elements_array.append("<gpxdata:hr>%s</gpxdata:hr>"  %(str(retrieve_value_for_display(point_datas['extras'],'heart_rate')[0])))
        trkpoint_elements_array.append("</gpxtpx:TrackPointExtension>")
        trkpoint_elements_array.append("</extensions>")
        trkpoint_elements_array.append("</trkpt>")
        if len(trkpoint_elements_array) > 0:
            return u'\n'.join(trkpoint_elements_array) #circles à traduire en degrés cf. Vasilev !!!
        else: 
            return None

for fpath in filenames:
    if infos:
        print ('##### %s ' % fpath).ljust(60, '#')
        

    print_hook_func = None
    if infos:
        print_hook_func = print_record
    else:
        print_hook_func = return_gpx_trk_entry

    record_number = 0
    a = Activity(fpath)
    fxpath = "%s.gpx" %(fpath)
    name=basename(fpath)
    fdate=datetime.strptime(name, "%Y-%m-%d-%H-%M-%S.fit")
    start_date_activity = ""
    if fdate is not None:
       start_date_activity = datetime.strftime(fdate,"%Y-%m-%sT%H:%M:%SZ")
    #begin the GPX File !!!
    with open(fxpath, 'rt') as f:
        print ("<?xml version=\"1.0\" encoding=\"UTF-8\"?>")
        print ("<gpx creator=\"jpmena\"")
        print (" xmlns:gpxtrx=\"http://www.garmin.com/xmlschemas/GpxExtensions/v3\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"")
        print (" xmlns:gpxtpx=\"http://www.garmin.com/xmlschemas/TrackPointExtension/v1\"")
        print (" xmlns:gpxx=\"http://www.garmin.com/xmlschemas/WaypointExtension/v1\" xmlns:nmea=\"http://trekbuddy.net/2009/01/gpx/nmea\">")
        print ("<metadata>")
        print ("<time>%s</time>" %(start_date_activity))
        print ("</metadata>")
        print ("<trk>")
        print ("<name>%s</name>" %(name))
        print ("<trkseg>")
        map(affiche_trkpoinnt, a.parse(hook_func=print_hook_func))
        print()
        print ("</trkseg>")
        print ("</trk>")
        print ("</gpx>")
    #ends the GPX File !!!!
