import requests
import ConfigParser
import ht_util
from gitlab import Gitlab
from models import Tag


def get_tag_info():
    while Tag.ref != 'test' and Tag.ref != "master":
        Tag.ref = raw_input("Please enter branch name for building the tag (test|master): ")

    while not Tag.name.startswith("v"):
        Tag.name = raw_input("Please enter tag name, tag name should start with v: ")

    Tag.message = raw_input("Please enter tag message: ")
    Tag.release_desp = raw_input("Please enter the release description: ")

project_dict = {'agz-business': 67, 'agz-web-design': 64, 'agz-web-runtime': 65, 'agzplatform': 124,
                'agzSystemRuntime': 75, 'agz-message': 126, 'glossary': 114, 'agz-reportsql': 130,
                'ht_util': 33, 'agz-cache': 69, 'agz-curator': 96, 'agz-dbaccess': 48,
                'agz-dubbo-proxy': 68, 'agz-business-api': 66, 'agz-tree': 119, 'agz-bo': 145}

config = ConfigParser.ConfigParser()
config.read('gitlab_util.conf')
gitlab_host = config.get('common', 'gitlab_host').rstrip('/')
private_token = config.get('common', 'private_token')

gitlab = Gitlab(gitlab_host, private_token)

get_tag_info()
tag_exists = False
tag_create_list = []

for project_name, project_id in project_dict.items():
    tag = Tag()
    tag.prj_id = project_id
    tag.prj_name = project_name
    tag_create_list.append(tag)

    if gitlab.is_tag_exists(tag):
        tag_exists = True
        print "tag can not be created at " + project_name

if tag_exists:
    raise SystemExit("Tag can not be created")

print "Will create tag [{0}] on branch [{1}] for following projects: \n{2} "\
                        .format(tag.name, tag.ref, project_dict.keys())

ht_util.ask_for_confirmation()

for tag in tag_create_list:
    gitlab.create_tag(tag)

