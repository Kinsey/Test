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


def accept_mergerequest(project_id, mergerequest_id):
    """auto accept an existing merge request.

    :param project_id: ID of the project originating the merge request
    :param mergerequest_id: ID of the merge request to accept
    :return: dict of the modified merge request
    """
    data = dict(
        private_token=private_token,
    )

    resp = requests.put('{0}/{1}/merge_request/{2}/merge'.format(projects_url, project_id, mergerequest_id),
                        params=data)
    if resp.status_code == 200:
        return resp.json()
    else:
        return str(resp.status_code) + ' ' + resp.text


config = ConfigParser.ConfigParser()
config.read('gitlab_config.conf')

basic_section = 'basic'
gitlab_host = config.get(basic_section, 'gitlab_host').rstrip('/')
private_token = config.get(basic_section, 'private_token')
source_branch = config.get(basic_section, 'source_branch')
target_branch = config.get(basic_section, 'target_branch')

projects_url = gitlab_host + '/api/v3/projects'

project_id = 67
project_name = 'agz-bussiness'

# Get all opened merge request for specific project
merge_request_list = get_mergerequests(project_id, state='opened')
if merge_request_list:
    for i in merge_request_list:
        if i['source_branch'] == source_branch and i['target_branch'] == target_branch and i[
            'merge_status'] == 'can_be_merged':
            print accept_mergerequest(project_id, i['id'])
        else:
            print 'skip merge due to merge status unchecked, project_name={0}'.format(project_name)

else:
    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    data = create_mergerequest(project_id, source_branch, target_branch, title=project_name + '_' + now)
    if data['merge_status'] == 'can_be_merged':
        print accept_mergerequest(project_id, data['id'])
    else:
        print data['merge_status']
