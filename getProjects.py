import requests
import json


gitlab_url="http://192.168.233.137/api/v3"
token = 'private_token=oR_a6hh1zHfftvzZXCW6'

req = requests.get(gitlab_url + '/projects?'+ token + '&per_page=3')

if(req.status_code==200):
    data = req.json()
    print data
    print type(data)
    for i in data:
        print i[u'name'] + ' = '+ str(i[('id')])

else:
    print req.text


