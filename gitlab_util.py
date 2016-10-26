import requests
import datetime
import ConfigParser
import logging
import sys
import os
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
        state=state,
    )
    try:
        resp = requests.get('{0}/{1}/merge_requests'.format(projects_url, project_id), params=params)
        resp.raise_for_status()
    except requests.RequestException as e:
        logging.warning(e)
    else:
        return resp.json()


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
        logging.warning(e)
    else:
        logging.info('Merge request created, title={0}'.format(title))
        return resp.json()


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
    logging.info('merge request accepted, name={0}'.format(mergerequest_title))
    return resp.json()

# **************************  start  *****************************
script_name = os.path.basename(sys.argv[0])
script_version = '0.1'

# set logging to log file
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='gitlab_util.log',
                    filemode='a')

# set logging to console console
console = logging.StreamHandler()
console.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

# set requests warning level
logging.getLogger("requests").setLevel(logging.WARNING)

logging.info("Start {0}, version={1}".format(script_name, script_version))

config = ConfigParser.ConfigParser()
config.read('gitlab_util.conf')

# load merge_branches from gitlab_util.conf
merge_branches_list = config.sections()
merge_branches_list.remove('common')
merge_branches_list_len = len(merge_branches_list)

print "Start {0} start, version={1}".format(script_name, script_version)

# get gitlab url and private token from gitlab_util.conf
gitlab_host = config.get('common', 'gitlab_host').rstrip('/')
private_token = config.get('common', 'private_token')

# print interactive menu
index = 1
print "****Please Enter Your Choice: [1]-[{0}]****".format(merge_branches_list_len)
for mb in merge_branches_list:
    print '('+ str(index) + ') ' + mb
    index += 1

chosen_mb_index = int(raw_input("Please pick up a merge type [1]-[{0}]: ".format(merge_branches_list_len)))

while chosen_mb_index < 1 or chosen_mb_index >= index:
    chosen_mb_index = int(raw_input("input invalid, please pick up a merge type [1]-[{0}]: "
                                    .format(merge_branches_list_len)))

merge_branches = merge_branches_list[chosen_mb_index-1]

# print detailed information for confirmation
source_branch = config.get(merge_branches, 'source_branch')
target_branch = config.get(merge_branches, 'target_branch')
project_list = config.get(merge_branches, 'project_list').split(',')

print ""
print "**** Detailed information for " + merge_branches + " ****"
print "project_list = " + str(project_list)
print "source_branch = " + source_branch
print "target_branch = " + str(target_branch)

proceed = raw_input("Is this ok? [yes/no]: ")
if proceed != "yes":
    print "exit due to user quit"
    logging.info("exit due to user quit")
    exit()

logging.info("gitlab_host = " + gitlab_host)
logging.info("merge_branches = " + merge_branches)
logging.info("project_list = " + str(project_list))
logging.info("source_branch = " + source_branch)
logging.info("target_branch = " + str(target_branch))

projects_url = gitlab_host + '/api/v3/projects'

project_dict = {'agz-business': 67, 'agz-web-design': 64, 'agz-web-runtime': 65, 'agzplatform': 124,
                'agzSystemRuntime': 75, 'agz-message': 126, 'glossary': 114, 'agz-reportsql':130,
                'ht_util': 33, 'agz-cache': 69,'agz-curator': 96,'agz-dbaccess': 48,
                'agz-dubbo-proxy': 68, 'agz-business-api':66, 'agz-tree':119}

#Configure pretty table for human readable
result_table = PrettyTable(["Project name", "Merge request", "Merge request type", "Number of commits", "Merge status"])
result_table.align["Project name"] = "l"  # Left align city names
result_table.padding_width = 1  # One space between column edges and contents (default)

mergerequest_to_be_merged = []

for project_name in project_list:
    project_id = project_dict[project_name]

    logging.info("Processing merge request for project {0}".format(project_name))

    legacy_mergerequest_not_found = True
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
                    legacy_mergerequest_not_found = False
                    logging.info('Legacy merge request found, name={0}, merge_status={1}'
                                 .format(mergerequest_title, mergerequest_status))

        # No legacy merge request, create new merge request
        if legacy_mergerequest_not_found:
            logging.info("No legacy merge request found, create merge request for project {0}"
                          .format(project_name))
            mergerequest_title = project_name + '_' + merge_branches
            data = create_mergerequest(project_id, source_branch, target_branch, title=mergerequest_title)
            mergerequest_id = data['id']
            mergerequest_status = data['merge_status']
            mergerequest_type = 'new'
    except Exception as e:
        logging.warning(e)

    num_of_commits = len(get_mergerequest_commits(project_id, mergerequest_id))

    if num_of_commits:
        try:
            accept_mergerequest(project_id, mergerequest_id)
        except requests.RequestException as e:
            result_table.add_row(
                [project_name, mergerequest_title, mergerequest_type, num_of_commits, "cannot_be_merged"])
            logging.warning(e)
        else:
            result_table.add_row([project_name, mergerequest_title, mergerequest_type, num_of_commits, "merged"])
    else:
        logging.info('No commits for {0}, auto merge skipped'.format(mergerequest_title))
        result_table.add_row([project_name, mergerequest_title, mergerequest_type, num_of_commits, 'skipped'])

logging.info(result_table)
print result_table