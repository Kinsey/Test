import requests
import ConfigParser
import logging
import sys
import os
from prettytable import PrettyTable
import ht_util
from gitlab import Gitlab
from models import Project, Mergerequest

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

gitlab_host = config.get('common', 'gitlab_host').rstrip('/')
private_token = config.get('common', 'private_token')
gitlab = Gitlab(gitlab_host, private_token)

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

source_branch = config.get(merge_branches, 'source_branch')
target_branch = config.get(merge_branches, 'target_branch')
project_list = config.get(merge_branches, 'project_list').split(',')

Mergerequest.src_branch = source_branch
Mergerequest.tgt_branch = target_branch

print ""
print "**** Detailed information for " + merge_branches + " ****"
print "project_list = " + str(project_list)
print "source_branch = " + source_branch
print "target_branch = " + str(target_branch)

ht_util.ask_for_confirmation()

logging.info("gitlab_host = " + gitlab_host)
logging.info("merge_branches = " + merge_branches)
logging.info("project_list = " + str(project_list))
logging.info("source_branch = " + source_branch)
logging.info("target_branch = " + str(target_branch))

projects_url = gitlab_host + '/api/v3/projects'

project_dict = {'agz-business': 67, 'agz-web-design': 64, 'agz-web-runtime': 65, 'agzplatform': 124,
                'agzSystemRuntime': 75, 'agz-message': 126, 'glossary': 114, 'agz-reportsql':130,
                'ht_util': 33, 'agz-cache': 69,'agz-curator': 96,'agz-dbaccess': 48,
                'agz-dubbo-proxy': 68, 'agz-business-api':66, 'agz-tree':119, 'agz-bo':145}

# Configure pretty table for human readable
result_table = PrettyTable(["Project name", "Merge request", "Merge request type", "Number of commits", "Merge status"])
result_table.align["Project name"] = "l"  # Left align project names
result_table.padding_width = 1  # One space between column edges and contents (default)

mergerequest_to_be_merged = []

for project_name in project_list:
    project_id = project_dict[project_name]
    project = Project()
    project.prj_name = project_name
    project.prj_id = project_dict[project_name]

    mr = Mergerequest()
    mr.project = project

    logging.info("Processing merge request for project {0}".format(project_name))

    legacy_mergerequest_not_found = True
    try:
        # Check if there is any legacy merge request
        legacy_mergerequest_list = gitlab.get_opened_mergerequests(project)
        if legacy_mergerequest_list:
            for i in legacy_mergerequest_list:
                if i['source_branch'] == source_branch and i['target_branch'] == target_branch:
                    mr.title = i['title']
                    mr.id = i['id']
                    mr.status = i['merge_status']
                    legacy_mergerequest_not_found = False
                    logging.info('Legacy merge request found, name={0}, merge_status={1}'
                                 .format(mr.title, mr.status))

        # No legacy merge request, create new merge request
        if legacy_mergerequest_not_found:
            logging.info("No legacy merge request found, create merge request for project {0}"
                          .format(project_name))
            mr.title = project_name + '_' + merge_branches
            data = gitlab.create_mergerequest(mr)
            mr.id = data['id']
            mr.status = data['merge_status']
    except Exception as e:
        logging.warning(e)

    mr.num_of_commits = gitlab.get_mergerequest_commits(mr)

    if mr.num_of_commits:
        try:
            accept_mergerequest(mr)
        except requests.RequestException as e:
            result_table.add_row(
                [mr.project.prj_name, mr.title, mr.type, mr.num_of_commits, "cannot_be_merged"])
            logging.warning(e)
        else:
            result_table.add_row([project_name, mr.title, mr.title, mr.num_of_commits, "merged"])
    else:
        logging.info('No commits for {0}, auto merge skipped'.format(mr.title))
        result_table.add_row([project_name, mr.title, mr.title, mr.num_of_commits, 'skipped'])

logging.info(result_table)
print result_table
