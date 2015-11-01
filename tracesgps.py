#!/usr/bin/env python
# coding: utf-8 


import datetime
from google.appengine.ext import blobstore #cf. https://github.com/GoogleCloudPlatform/appengine-blobstore-python/blob/master/main.py
from google.appengine.ext.webapp import blobstore_handlers
import calendar
import jinja2
import os
import webapp2
from gpxparse import GpxHandler
from fitutils import GaeBlobStoreDatas
from webapp2_extras import json
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
    
class MainPage(webapp2.RequestHandler):
    def get(self):
        current_time = datetime.datetime.now()
        upload_url = blobstore.create_upload_url('/upload_gpx_data')
        template = JINJA_ENVIRONMENT.get_template('home.html')
        context = {
                   'ajourdhui': current_time,
                   'upload_url': upload_url
        }
        self.response.out.write(template.render(context))
        
# [START upload_handler]
class TracesUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        try:
            upload = self.get_uploads()[0]

            self.redirect('/traces/%s' % upload.key())
            
        except:
            self.error(404)
# [END upload_handler]
        
class TraceCalcultationHandler(webapp2.RequestHandler):
    def get(self, photo_key):
        blobstore_gpx_infos = blobstore.get(photo_key)
        if not blobstore_gpx_infos:
            self.error(404)
        else: 
            uploaded_file = blobstore_gpx_infos.__dict__['_BlobInfo__entity']
            #other solution nom_fic_gpx = blobstore_gpx_infos.filename #https://cloud.google.com/appengine/docs/python/blobstore/blobinfoclass
            blob_reader = blobstore.BlobReader(photo_key, buffer_size=1048576) #https://cloud.google.com/appengine/docs/python/blobstore/blobreaderclass
            performance_filename = uploaded_file['filename']
            vitesse_moyenne = 0
            donnees_vitesse = [];
            grap_meta_datas = {'xtitle':"Heure et minute de l'effort", 'ytitle':"vitesse (km/h)"}
            distance_parcourue = 0
            if performance_filename.endswith('.gpx'):
                xml_str_content = ""
                for line in blob_reader:
                    xml_str_content += line
                #todo: prévoir une condition le contenu n'est pas vide ?
                handler = GpxHandler()
                array_results = handler.traduction_gpx_vers_csv(xml_str_content) #{'iplot':iout_path,'lplot':lout_path,'donnees':avancees}
                
                for res_dict in array_results:
                    donnees_vitesse.append([calendar.timegm(res_dict['t'].timetuple()) * 1000,res_dict['vl']*3.6]) #https://flot.googlecode.com/svn/trunk/API.txt timestaps in milliseconds
                    vitesse_moyenne += res_dict['vl']
                vitesse_moyenne = vitesse_moyenne/len(array_results)
                distance_parcourue = array_results[-1]['dc']
            elif performance_filename.endswith('.fit'):
                handler=GaeBlobStoreDatas(blob_reader)
                array_results = handler.parse(hook_func=handler.transform_fitpoint_entry)
                nbpoints = 0
                for res_dict in array_results:
                    json_dict = res_dict['json']
                    if json_dict is not None:
                        nbpoints+=1
                        donnees_vitesse.append([json_dict['timestamp'][0], json_dict['speed'][0]]) #https://flot.googlecode.com/svn/trunk/API.txt timestaps in milliseconds
                        vitesse_moyenne += json_dict['speed'][0]
                        distance_parcourue = json_dict['total_distance'][0]
                vitesse_moyenne = vitesse_moyenne/nbpoints
            #http://stackoverflow.com/questions/12664696/how-to-properly-output-json-with-app-engine-python-webapp2
            json_results = {
                       'fichier': performance_filename,# TODO corriger how to make a query !!!!
                       'speed_datas': donnees_vitesse,
                       'graph_metas' : grap_meta_datas,
                       'average_speed': vitesse_moyenne,
                       'distance':distance_parcourue
            }
            self.response.content_type = 'application/json'
            self.response.write(json.encode(json_results))

application = webapp2.WSGIApplication([(r'/', MainPage), (r'/upload_gpx_data', TracesUploadHandler),(r'/traces/(.+)$', TraceCalcultationHandler)],
debug=True)

