import gitlab

hongtoo_gitlab = gitlab.Gitlab("http://192.168.2.224/", "4RYr-9ymMchXwzgqh5Fz")
print hongtoo_gitlab.get_projects()