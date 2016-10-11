import requests
import datetime
import ConfigParser
import logging
import sys
from prettytable import PrettyTable


def get_projects():
    """Returns a dictionary of all the projects

        :return: list with the repo name, description, web url, ssh url
        """
    params = dict(
        per_page=200,
        private_token=private_token
    )
    resp = requests.get(projects_url, params=params)
    if resp.status_code == 200:
        return resp.json()
    else:
        raise Exception(resp.status_code, resp.text)


def get_mergerequests(project_id, state=None):
    """Get all the merge requests for a project.

        :param project_id: ID of the project to retrieve merge requests for
        :param state: Passes merge request state to filter them by it
        :return: List with all the merge requests
        """
    params = dict(
        per_page=20,
        private_token=private_token,
        state=state
    )
    resp = requests.get('{0}/{1}/merge_requests'.format(projects_url, project_id), params=params)
    if resp.status_code == 200:
        return resp.json()
    else:
        raise Exception(resp.status_code, resp.text)


def get_mergerequest_commits(project_id, mergerequest_id):
    """Get commits of a merge request.

    :param project_id: ID of the project
    :param mergerequest_id: ID of the merge request
    :return: numbers of specified merge request commits
    """
    params = dict(
        private_token=private_token,
    )
    resp = requests.get('{0}/{1}/merge_request/{2}/commits'.format(projects_url, project_id, mergerequest_id),
                        params=params)

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
    params = dict(
        private_token=private_token,
        source_branch=source_branch,
        target_branch=target_branch,
        title=title
    )

    try:
        resp = requests.post('{0}/{1}/merge_requests'.format(projects_url, project_id), params=params)
        resp.raise_for_status()
    except requests.RequestException as e:
        print e
    else:
        return resp.json()

    # if resp.status_code == 201:
    #     logging.info('Merge request created, title={0}'.format(title))
    #     return resp.json()
    # else:
    #     logging.warning('create merge request failed', str(resp.status_code), resp.text, title)
    #
    #     raise Exception('create merge request failed', str(resp.status_code), resp.text, title)


def accept_mergerequest(project_id, mergerequest_id):
    """auto accept an existing merge request.

    :param project_id: ID of the project originating the merge request
    :param mergerequest_id: ID of the merge request to accept
    :return: dict of the modified merge request
    """
    params = dict(
        private_token=private_token,
    )

    resp = requests.put('{0}/{1}/merge_request/{2}/merge'.format(projects_url, project_id, mergerequest_id),
                        params=params)
    resp.raise_for_status()

    return resp.json()
    # if resp.status_code == 200:
    #     logging.info('merge request accepted, name={0}'.format(mergerequest_title))
    #     return resp.json()
    # else:
    #     raise Exception('accept merge request failed', str(resp.status_code), resp.text)


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='gitlab_util.log',
                    filemode='a')

logging.getLogger("requests").setLevel(logging.WARNING)

# Print log to console
console = logging.StreamHandler()
console.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

logging.info('\n\n')
logging.info("Merge start")

config = ConfigParser.ConfigParser()
config.read('gitlab_util.conf')

merge_branches = 'dev-to-test'
gitlab_host = config.get('common', 'gitlab_host').rstrip('/')
private_token = config.get('common', 'private_token')
source_branch = config.get(merge_branches, 'source_branch')
target_branch = config.get(merge_branches, 'target_branch')
project_list = config.get(merge_branches, 'project_list').split(',')

logging.info("gitlab_host = " + gitlab_host)
logging.info("merge_branches = " + merge_branches)
logging.info("project_list = " + str(project_list))



projects_url = gitlab_host + '/api/v3/projects'

project_dict = {'agz-business': 67, 'agz-web-design': 64, 'agz-web-runtime': 65, 'agzplatform': 124,
                'agzSystemRuntime': 75, 'agz-message': 126, 'glossary': 114}

# Configure prettytable for human readable
result_table = PrettyTable(["Project name", "Merge request", "Merge request type", "Number of commits", "Merge status"])
result_table.align["Project name"] = "l"  # Left align city names
result_table.padding_width = 1  # One space between column edges and contents (default)

mergerequest_to_be_merged = []

for project_name in project_list:
    project_id = project_dict[project_name]

    logging.info("Start process merge request for project {0}".format(project_name))

    try:
        # Check if there is any legacy merge request
        legacy_mergerequest_list = get_mergerequests(project_id, state='opened')
        if legacy_mergerequest_list:
            for i in legacy_mergerequest_list:
                if i['source_branch'] == source_branch and i['target_branch'] == target_branch:
                    mergerequest_title = i['title']
                    mergerequest_id = i['id']
                    mergerequest_status = i['merge_status']
                    mergerequest_type = 'legacy'
                    logging.info('Legacy merge request found, name={0}, merge_status={1}'
                                 .format(mergerequest_title, mergerequest_status))

        # No legacy merge request, create new merge request
        else:
            cur_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            mergerequest_title = project_name + '_' + cur_time
            data = create_mergerequest(project_id, source_branch, target_branch, title=mergerequest_title)
            mergerequest_id = data['id']
            mergerequest_status = data['merge_status']
            mergerequest_type = 'new'

        mergerequest_to_be_merged.append(
            dict(project_id=project_id, project_name=project_name, mergerequest_title=mergerequest_title,
                 mergerequest_id=mergerequest_id, mergerequest_status=mergerequest_status,
                 mergerequest_type=mergerequest_type))
    except Exception as e:
        print e.message

logging.debug(mergerequest_to_be_merged)

# Process collected merge request
for mr in mergerequest_to_be_merged:
    project_id = mr['project_id']
    project_name = mr['project_name']
    mergerequest_id = mr['mergerequest_id']
    mergerequest_title = mr['mergerequest_title']
    mergerequest_status = mr['mergerequest_status']
    mergerequest_type = mr['mergerequest_type']

    num_of_commits = len(get_mergerequest_commits(project_id, mergerequest_id))

    if num_of_commits:
        if mergerequest_status == "cannot_be_merged":
            result_table.add_row([project_name, mergerequest_title, mergerequest_type,
                                  num_of_commits, mergerequest_status])
            continue

        accept_mergerequest(project_id, mergerequest_id)

        result_table.add_row([project_name, mergerequest_title, mergerequest_type, num_of_commits, "merged"])

    else:
        logging.info('No commits for {0}, auto merge skipped'.format(mergerequest_title))
        result_table.add_row([project_name, mergerequest_title, mergerequest_type, num_of_commits, 'skipped'])

logging.info("Printing merge results")
logging.info(result_table)
logging.info("Merge end")

print  result_table

