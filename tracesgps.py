#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
import datetime
import calendar
import jinja2
import os
import webapp2
from GPXHandler import traduction_gpx_vers_csv
from webapp2_extras import json
template_env = jinja2.Environment(
loader=jinja2.FileSystemLoader(os.getcwd()))
class MainPage(webapp2.RequestHandler):
    def get(self):
        current_time = datetime.datetime.now()
        template = template_env.get_template('home.html')
        context = {
                   'ajourdhui': current_time,
        }
        self.response.out.write(template.render(context))
        
class TraceHandler(webapp2.RequestHandler):
    def get(self, fichier_gpx):
        array_results = traduction_gpx_vers_csv("data/{0}".format(fichier_gpx)) #{'iplot':iout_path,'lplot':lout_path,'donnees':avancees}
        vitesse_moyenne = 0
        donnees_vitesse = []
        for res_dict in array_results:
            donnees_vitesse.append([calendar.timegm(res_dict['t'].timetuple()) * 1000,res_dict['vl']]) #https://flot.googlecode.com/svn/trunk/API.txt timestaps in milliseconds
            vitesse_moyenne += res_dict['vl']
        vitesse_moyenne = vitesse_moyenne/len(array_results)
        distance_parcourue = array_results[-1]['dc']
        #http://stackoverflow.com/questions/12664696/how-to-properly-output-json-with-app-engine-python-webapp2
        json_results = {
                   'fichier': fichier_gpx,
                   'speed_datas': donnees_vitesse,
                   'average_speed': vitesse_moyenne,
                   'distance':distance_parcourue
        }
        self.response.content_type = 'application/json'
        self.response.write(json.encode(json_results))

application = webapp2.WSGIApplication([('/', MainPage),('/traces/(.+\.gpx)', TraceHandler)],
debug=True)

