import requests
import datetime
import ConfigParser


def get_projects():
    """Returns a dictionary of all the projects

        :return: list with the repo name, description, web url, ssh url
        """
    data = dict(
        per_page=200,
        private_token=private_token
    )
    resp = requests.get(projects_url, params=data)
    if resp.status_code == 200:
        return resp.json()
    else:
        return str(resp.status_code) + ' ' + resp.text


def get_mergerequests(project_id, state=None):
    """Get all the merge requests for a project.

        :param project_id: ID of the project to retrieve merge requests for
        :param state: Passes merge request state to filter them by it
        :return: List with all the merge requests
        """
    data = dict(
        per_page=200,
        private_token=private_token,
        state=state
    )
    resp = requests.get('{0}/{1}/merge_requests'.format(projects_url, project_id), params=data)
    if resp.status_code == 200:
        return resp.json()
    else:
        return str(resp.status_code) + ' ' + resp.text


def get_mergerequest_commits(project_id, mergerequest_id):
    """Get commits of a merge request.

    :param project_id: ID of the project
    :param mergerequest_id: ID of the merge request
    :return: numbers of specified merge request commits
    """
    data = dict(
        private_token=private_token,
    )
    resp = requests.get('{0}/{1}/merge_request/{2}/commits'.format(projects_url, project_id, mergerequest_id),
                        params=data)

    if resp.status_code == 200:
        return resp.json()
    else:
        return str(resp.status_code) + ' ' + resp.text


def create_mergerequest(project_id, source_branch, target_branch, title):
    """Create a new merge request.

    :param project_id: ID of the project originating the merge request
    :param source_branch: name of the branch to merge from
    :param target_branch: name of the branch to merge to
    :param title: Title of the merge request
    :return: dict of the new merge request
    """
    data = dict(
        private_token=private_token,
        source_branch=source_branch,
        target_branch=target_branch,
        title=title
    )
    resp = requests.post('{0}/{1}/merge_requests'.format(projects_url, project_id), params=data)
    if resp.status_code == 201:
        return resp.json()
    else:
        return str(resp.status_code) + ' ' + resp.text

config = ConfigParser.ConfigParser()
config.read('gitlab_config.conf')

gitlab_host = config.get('basic', 'gitlab_host').rstrip('/')
private_token = config.get('basic', 'private_token')

api_url = gitlab_host + '/api/v3'
projects_url = api_url + "/projects"

project_id = 67
source_branch = 'dev'
target_branch = 'test'

#print get_mergerequests(67, state='opened')
#print len(get_mergerequest_commits(67, 977))
now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
print projects_url
print create_mergerequest(project_id, source_branch, target_branch, title='agz-business-'+ now)