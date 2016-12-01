import requests


class Gitlab:
    def __init__(self, host, token):
        self.host = host
        self.token = token
        self.api_url = self.host + "/api/v3"
        self.projects_url = self.api_url + "/projects"

    def get_projects(self, per_page=200):
        data = {'per_page': per_page, 'private_token': self.token}
        resp = requests.get(self.projects_url, params=data)
        resp.raise_for_status()
        return resp.json()

    def create_tag(self, tag):
        """add tag per release

        :param tag: tag to be create
        :return:
        """
        params = dict(
            private_token=self.token,
            ref=tag.ref,
            tag_name=tag.name,
            message=tag.message,
            release_description=tag.release_desp
        )
        resp = requests.post('{0}/{1}/repository/tags'.format(self.projects_url, tag.prj_id), params=params)
        if resp.status_code == 201:
            print 'tag created, name={0}, target_branch={1}, project_name={2}'.format(tag.name, tag.ref, tag.prj_name)
        else:
            print resp.text + " project_name=" + tag.prj_name + " response_code=" + str(resp.status_code)

    def is_tag_exists(self, tag):
        """verify if tag already exists in project

        :param tag: tag to be checked
        :return:
        """
        exists = False
        params = dict(
            private_token=self.token,
        )
        resp = requests.get('{0}/{1}/repository/tags/{2}'.format(self.projects_url, tag.prj_id, tag.name), params=params)
        if resp.status_code == 200:
            exists = True

        return exists
