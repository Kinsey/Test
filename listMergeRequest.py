import requests

gitlab_url="http://192.168.233.137/api/v3"
token = 'private_token=oR_a6hh1zHfftvzZXCW6'


#Get opened
req = requests.get(gitlab_url + '/projects/114/merge_requests?state=opened&'+ token + '&per_page=200&source_branch=testing&target_branch=master&title=xyz')

if(req.status_code==200):
    data = req.json()
    #merge_request_id =
    for i in data:

        merge_request_id = i['iid']
        print merge_request_id
        delete = requests.delete(gitlab_url + '/projects/114/merge_requests/134?'+ token)
        if(delete.status_code==200):
            print 'merge_request delete successeful'
else:
    print req.text

