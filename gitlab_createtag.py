import requests
import datetime
import ConfigParser
import logging
import sys
import os
from prettytable import PrettyTable


def isTagAvailable(project_id, tag):
    """verify if tag already exists in project

    :param project_id: ID of the project originating the merge request
    :return:
    """
    params = dict(
        private_token=private_token,
        #tag_name=tag
    )

    resp = requests.get('{0}/{1}/repository/tags/{2}'.format(projects_url, project_id, tag), params=params)

    if resp.status_code == 404:
        return True
    elif resp.status_code == 200:
        print "Tag {0} already exists in {1}".format(tag, project_name)
        return False
    else:
        print resp.text + " project_name=" + project_name + " response_code=" + str(resp.status_code)
        return False

def create_tag(project_id, tag):
    """add tag per release

    :param project_id: ID of the project originating the merge request
    :return:
    """
    params = dict(
        private_token=private_token,
        ref=target_branch,
        tag_name=tag
    )

    resp = requests.post('{0}/{1}/repository/tags'.format(projects_url, project_id), params=params)
    if resp.status_code == 201:
        print 'tag added, name={0}, target_branch={1}, project_name={2}'.format(tag, target_branch, project_name)
    else:
        print resp.text + " project_name=" + project_name + " response_code=" + str(resp.status_code)

project_dict = {'agz-business': 67, 'agz-web-design': 64, 'agz-web-runtime': 65, 'agzplatform': 124,
                'agzSystemRuntime': 75, 'agz-message': 126, 'glossary': 114, 'agz-reportsql':130,
                'ht_util': 33, 'agz-cache': 69,'agz-curator': 96,'agz-dbaccess': 48,
                'agz-dubbo-proxy': 68, 'agz-business-api':66, 'agz-tree':119, 'agz-bo':145}

# Get basic configurations
config = ConfigParser.ConfigParser()
config.read('gitlab_util.conf')
gitlab_host = config.get('common', 'gitlab_host').rstrip('/')
private_token = config.get('common', 'private_token')
projects_url = gitlab_host + '/api/v3/projects'
add_tag = True

target_branch = raw_input("Please enter branch name for building the tag (test|master): ")

while target_branch != 'test' and target_branch != "master":
    target_branch = raw_input("Please enter branch name for building the tag (test|master): ")

tag = raw_input("Please enter the tag name, start with v: ")

while not tag.startswith("v"):
    target_branch = raw_input("Please enter the tag name, tag name should start with v: ")

# if input tag exists in any project, then abort the tag create process
for project_name, project_id in project_dict.items():
    if not isTagAvailable(project_id, tag):
        add_tag = False

if add_tag:
    print "will create tag {0} from branch {1} for following projects: ".format(tag, target_branch)
    print project_dict.keys()

    proceed = raw_input("Is this ok? [yes/no]: ")
    if proceed != "yes":
        print "exit due to user quit"
        logging.info("exit due to user quit")
        exit()

    for project_name, project_id in project_dict.items():
        create_tag(project_id, tag)

