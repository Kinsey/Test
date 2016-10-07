import requests
import logging
import json

def acceptMergeRequest(projectId, mergeRequestId):
    resp = requests.put(gitlab_url + '/projects/114/merge_requests/'+ mergeRequestId + '/merge' + token)
    if (resp.status_code == 200):
        print 'success merged'
    else:
        print str(resp.status_code) + ' ' + resp.text

def createMergeRequest():


    return 111


gitlab_url="http://192.168.233.137/api/v3"
project_id=114
token='?private_token=oR_a6hh1zHfftvzZXCW6'

params = dict(
    target_branch='master',
    source_branch='testing',
    title='GlossaryMerge',
    #token = 'private_token=oR_a6hh1zHfftvzZXCW6'
)

#resp = requests.post(gitlab_url + '/projects/114/merge_requests?' + token + '&source_branch=testing&target_branch=master&title=GlossaryMerge')
resp = requests.post(gitlab_url + '/projects/114/merge_requests?private_token=oR_a6hh1zHfftvzZXCW6', params=params)
data = resp.json()

if(resp.status_code==201):
    #for i in data:
    mergeRequestId = str(data['id'])
    print 'Success created merge request'
    print 'Auto accepting merge request'
    acceptMergeRequest(mergeRequestId)
else:
   print resp.text


