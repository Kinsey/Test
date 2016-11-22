import requests


class Gitlab:
    def __init__(self, host, token):
        self.host = host
        self.token = token
        self.api_url = self.host + "/api/v3"
        self.projects_url = self.api_url + "/projects"

    def get_projects(self, per_page=200):
        data = {'per_page':per_page, 'private_token':self.token}
        resp = requests.get(self.projects_url, params=data)
        if resp.status_code == 200:
            return resp.json()
        else:
            raise Exception(resp.status_code, resp.text)