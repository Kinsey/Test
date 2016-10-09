import requests
import datetime
import ConfigParser
import logging


def get_projects():
    """Returns a dictionary of all the projects

        :return: list with the repo name, description, web url, ssh url
        """
    data = dict(
        per_page=200,
        private_token=private_token
    )
    resp = requests.get(projects_url, params=data)
    return resp.status_code, resp.json(), resp.text


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
    return resp.status_code, resp.json(), resp.text


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


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s---%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='gitlab_util.log',
                    filemode='a')

# Print log to console
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s---%(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

#*******************************   read configuration start ********************************
config = ConfigParser.ConfigParser()
config.read('gitlab_config.conf')

merge_type = 'dev-to-test'
gitlab_host = config.get('common', 'gitlab_host').rstrip('/')
private_token = config.get('common', 'private_token')
source_branch = config.get(merge_type, 'source_branch')
target_branch = config.get(merge_type, 'target_branch')
project_list = config.get(merge_type, 'project_list').split(',')


#*******************************   read configuration end ********************************

projects_url = gitlab_host + '/api/v3/projects'

project_id = 67
project_name = 'agz-business'

# Get all opened merge request for specific project
status_code, mergerequest_list, err_msg = get_mergerequests(project_id, state='opened')
if status_code == 200:
    if mergerequest_list:
        for i in mergerequest_list:
            if i['source_branch'] == source_branch and i['target_branch'] == target_branch \
                    and i['merge_status'] == 'can_be_merged':
                print accept_mergerequest(project_id, i['id'])
            else:
                logging.info('skip merge due to merge status {0}, project_name={1}'\
                             .format(i['merge_status'], project_name))

    else:
        now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        data = create_mergerequest(project_id, source_branch, target_branch, title=project_name + '_' + now)
        if data['merge_status'] == 'can_be_merged':
            print accept_mergerequest(project_id, data['id'])
        else:
            print data['merge_status']
else:
    logging.warning("Get merge request failed, project_name={0}, status_code={1}, err_msg={2}"\
                    .format(project_name, str(status_code), err_msg))
