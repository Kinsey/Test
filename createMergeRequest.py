import requests
import datetime
import logging
import json

def acceptmergerequest(projectId, mergeRequestId):
    resp = requests.put(gitlab_url + '/projects/114/merge_requests/'+ mergeRequestId + '/merge' + token)
    if (resp.status_code == 200):
        print 'success merged'
    else:
        print str(resp.status_code) + ' ' + resp.text

gitlab_url="http://192.168.2.229/api/v3"
project_id=67
#token='?private_token=kYUL67sQhTqD6Ro6eHwN'

now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")


params = dict(
    target_branch='test',
    source_branch='dev',
    title='GlossaryMerge-'+now,
    private_token='kYUL67sQhTqD6Ro6eHwN'
)


#resp = requests.post(gitlab_url + '/projects/114/merge_requests?' + token + '&source_branch=testing&target_branch=master&title=GlossaryMerge')
resp = requests.post(gitlab_url + '/projects/67/merge_requests', params=params)
data = resp.json()
print type(data)

if(resp.status_code==201):
    #for i in data:
    mergeRequestId = str(data['id'])
    print 'Success created merge request' + mergeRequestId
   # print 'Auto accepting merge request'
    #acceptmergerequest(mergeRequestId)
else:
   #merge_status = data['merge_status']
   print resp.text


