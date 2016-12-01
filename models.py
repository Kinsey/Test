class Tag:
    name = ''
    message = ''
    release_desp = ''
    ref = ''

    def __init__(self):
        self.prj_id = 0
        self.prj_name = ''


class Project:
    def __init__(self):
        self.prj_id = 0
        self.prj_name = ''


class Mergerequest:
    src_branch = ''
    tgt_branch = ''

    def __init__(self):
        self.id = 0
        self.status = ''
        self.title = ''
        self.prj_id = 0
        self.prj_name = ''
        self.project = None
        self.num_of_commits = 0


