#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
import datetime
import jinja2
import os
import webapp2
from GPXHandler import traduction_gpx_vers_csv
template_env = jinja2.Environment(
loader=jinja2.FileSystemLoader(os.getcwd()))
class MainPage(webapp2.RequestHandler):
    def get(self):
        current_time = datetime.datetime.now()
        array_results = traduction_gpx_vers_csv("data/aulnay le 11 mars 2015.gpx") #{'iplot':iout_path,'lplot':lout_path,'donnees':avancees}
        vitesse_moyenne = 0
        for res_dict in array_results:
            vitesse_moyenne += res_dict['vl']
        vitesse_moyenne = vitesse_moyenne/len(array_results)*3.6
        distance_parcourue = array_results[-1]['dc']/1000.0
        template = template_env.get_template('home.html')
        context = {
        'distance_parcourue': distance_parcourue,
        'vitesse_moyenne': vitesse_moyenne
        }
        self.response.out.write(template.render(context))

application = webapp2.WSGIApplication([('/', MainPage)],
debug=True)
