import requests
import logging
import json

gitlab_url="http://192.168.233.137/api/v3"
token = 'private_token=oR_a6hh1zHfftvzZXCW6'

req = requests.put(gitlab_url + '/projects/114/merge_requests/978/merge?'+ token )
data = req.json()

if(req.status_code==200):
    #for i in data:
    print 'success'

else:
   print str(req.status_code) + ' ' + req.text
