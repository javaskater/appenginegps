'''
Created on 30 oct. 2015

@author: jpmena
'''

from __builtin__ import isinstance
from math import pow
from datetime import datetime
from fitparse import Activity
from __builtin__ import isinstance
from google.appengine.ext.blobstore import BlobReader

class GaeBlobStoreDatas(Activity):
    def __init__(self, gae_blob):
        if gae_blob is not None and isinstance(gae_blob, BlobReader) :
            self._file = gae_blob
            self._file_size = gae_blob.blob_info.size
            self._data_read = 0
            self._crc = 0
    
            self._last_timestamp = None
            self._global_messages = {}
            self.definitions = []
            self.records = []
    
    #transform a datetime into <time>2015-09-26T10:40:29Z</time> see Vasilev output
    def datetime_to_gpstimestamps(self, datetime_object):
        gps_timestamp = ""
        if isinstance(datetime_object, datetime):
            gps_timestamp = datetime_object.strftime("%Y-%m-%dT%H:%M:%SZ")
        return gps_timestamp
    
    
    #// degrees = semicircles * ( 180 / 2^31 ) see Vasilev program
    def semicircle_to_coordinates(self, semicircles):
        return float(semicircles) * 180 / pow(2, 31)
    
    
    #transform a speed in meters/seconds into a speed in km/hour
    def msecconds_to_kmhours(self, speed_ms):
        return speed_ms * 3.6
    
    
    #from the Python recipes p 31/252 - 10 
    #TODO : add conversion function and formatting function for dates - by default None function cf. base !!!!!!!!     
    def retrieve_value_for_display(self, values, key, converter=None, default=("","%s")):
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
    
    def transform_fitpoint_entry(self, rec, ):
        if rec.type.name == "record":
            fit_datas={'timestamp':None,'position_long':None,'position_lat':None,'elevation':None,'extras':{'speed':None,'distance':None,'heart_rate':None}}
            json_datas={'timestamp':None, 'speed':None, 'total_distance':None, 'heart_rate':None}
            for field in rec.fields:
                if field.name == 'timestamp':
                    fit_datas['timestamp']=field.data
                elif field.name == 'position_lat':
                    fit_datas['position_lat']=field.data
                elif field.name == 'position_long':
                    fit_datas['position_long']=field.data
                elif field.name == 'altitude':
                    fit_datas['altitude']=field.data
                elif field.name == 'speed':
                    fit_datas['extras']['speed']=field.data
                elif field.name == 'distance':
                    fit_datas['extras']['distance']=field.data
                elif field.name == 'heart_rate':
                    fit_datas['extras']['heart_rate']=field.data
                    
            fit_datas['position_long'] = self.retrieve_value_for_display(fit_datas,'position_long',converter=self.semicircle_to_coordinates)
            fit_datas['position_lat'] = self.retrieve_value_for_display(fit_datas,'position_lat',converter=self.semicircle_to_coordinates)
            json_datas['timestamp'] = self.retrieve_value_for_display(fit_datas,'timestamp')
            json_datas['speed'] = self.retrieve_value_for_display(fit_datas,'speed', converter=self.msecconds_to_kmhours)
            json_datas['total_distance'] = self.retrieve_value_for_display(fit_datas,'distance')
            json_datas['heart_rate'] = self.retrieve_value_for_display(fit_datas,'heart_rate')
            return {'fit':fit_datas, 'json':json_datas}
        else:
            return {'fit':None, 'json':None}
            


if __name__ == '__main__':
    pass