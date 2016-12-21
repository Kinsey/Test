import ssh
import sys
import time


def flush_redis(env):
    myclient = ssh.SSHClient()
    myclient.set_missing_host_key_policy(ssh.AutoAddPolicy())
    myclient.connect(basic_info[env]['redis_host'], port=22, username="root", password=basic_info[env]['password'])
    myclient.exec_command("service redis start")
    time.sleep(2)
    stdin, stdout, stderr = myclient.exec_command("redis-cli flushall")
    print basic_info[env]['redis_host'] + ": flushing redis..." + stdout.read().lower()


def restart_mycat(env):
    myclient = ssh.SSHClient()
    myclient.set_missing_host_key_policy(ssh.AutoAddPolicy())
    myclient.connect(basic_info[env]['mycat_host'], port=22, username="root", password=basic_info[env]['password'])
    print "restarting mycat..."
    myclient.exec_command(basic_info[env]['mycat_restart_cmd'])
    time.sleep(2)
    stdin, stdout, stderr = myclient.exec_command(basic_info[env]['mycat_status_cmd'])
    print basic_info[env]['mycat_host'] + ": " + stdout.read()

basic_info = {'dev01': {'password':'111111',
                         'redis_host':'dev01.demo.com',
                         'mycat_host': "dev01.demo.com",
                         'mycat_restart_cmd': "service mycat restart",
                         'mycat_status_cmd': "service mycat status",
                         },
               'tev02': {'password':'hongtoo123!',
                          'redis_host':'mycat02.demo.com',
                          'mycat_host': "mycat02.demo.com",
                          'mycat_restart_cmd': "/home/mycat/bin/mycat restart",
                          'mycat_status_cmd': "/home/mycat/bin/mycat status",
                         },
                'cp01': {'password':'hongtoo123!',
                          'redis_host':'mycat01.demo.com',
                          'mycat_host': "mycat01.demo.com",
                          'mycat_restart_cmd': "service mycat restart",
                          'mycat_status_cmd': "service mycat status",
                         },
                'cp02': {'password':'111111',
                          'redis_host':'cp02.demo.com',
                          'mycat_host': "cp02.demo.com",
                          'mycat_restart_cmd': "service mycat restart",
                          'mycat_status_cmd': "service mycat status",
                         },
                'testjk': {'password':'hongtoo123!',
                          'redis_host':'testjk.demo.com',
                          'mycat_host': "testjk.demo.com",
                          'mycat_restart_cmd': "service mycat restart",
                          'mycat_status_cmd': "service mycat status",
                         },
              }

if sys.argv[1] in basic_info.keys():
    flush_redis(sys.argv[1])
    restart_mycat(sys.argv[1])
elif sys.argv[1] == 'lb01':
    print "lb01 is not supported, please flush the services manually"
else:
    print "Unknown environment"
