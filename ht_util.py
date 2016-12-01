import ConfigParser


def ask_for_confirmation():
    answer = raw_input("Is this ok? [yes/no]: ")

    if answer != "yes":
        print "exit due to user quit"
        exit()


def read_configuration(config_file_path):
    config = ConfigParser.ConfigParser()
    config.read(config_file_path)
    gitlab_host = config.get('common', 'gitlab_host').rstrip('/')
    private_token = config.get('common', 'private_token')
    projects_url = gitlab_host + '/api/v3/projects'
