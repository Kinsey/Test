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
            # TODO

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
        # TODO
        return exists

    def get_opened_mergerequests(self, project):
        return self.get_mergerequests(project, state='opened')

    def get_mergerequests(self, project, state=None):
        """Get all the merge requests for a project.

               :param project: project to retrieve merge requests info
               :param state: Passes merge request state to filter
               :return: List with all the merge requests
               """
        params = dict(
            per_page=20,
            private_token=self.token,
            state=state,
        )
        try:
            resp = requests.get('{0}/{1}/merge_requests'.format(self.projects_url, project.prj_name), params=params)
            resp.raise_for_status()
        except requests.RequestException as e:
            # TODO
            pass
        else:
            return resp.json()

    def get_mergerequest_commits(self, mergerquest):
        """Get commits of a merge request.

        :param mergerquest: mergerequest to be check
        :return: numbers of specified merge request commits
        """
        num_of_commits = 0
        params = dict(
            private_token=self.private_token,
        )
        resp = requests.get('{0}/{1}/merge_request/{2}/commits'.format(self.projects_url,
                            mergerquest.project.prj_id, mergerquest.id), params=params)

        if resp.status_code == 200:
            num_of_commits =  len(resp.json())
        else:
            # TODO
            print str(resp.status_code) + ' ' + resp.text
            num_of_commits = -1
        return num_of_commits

    def create_mergerequest(self, mergerequest):
        """Create a new merge request

         :param mergerequest: mergerequest to be created
         :return: dict of the new merge request
         """
        params = dict(
             private_token=self.token,
             source_branch=mergerequest.src_branch,
             target_branch=mergerequest.tgt_branch,
             title=mergerequest.title
         )
        try:
             resp = requests.post('{0}/{1}/merge_requests'.format(self.projects_url, mergerequest.project.prj_id),
                                  params=params)
             resp.raise_for_status()
        except requests.RequestException as e:
             #logging.warning(e)
           pass
        else:
             #logging.info('Merge request created, title={0}'.format(title))
             return resp.json()

    def accept_mergerequest(self, mergrequest):
        """auto accept an existing merge request.

        :param mergerequest: mergerequest to accept
        :return: dict of the modified merge request
        """
        params = dict(
            private_token=self.token,
        )

        resp = requests.put('{0}/{1}/merge_request/{2}/merge'.format(self.projects_url, mergrequest.id),
                            params=params)
        resp.raise_for_status()
        #TODO #logging.info('merge request accepted, name={0}'.format(mergequest.title))
        return resp.json()





