import datetime

def ex_tefdasfst():

    raise Exception("dfa")

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")



try:
    ex_tefdasfst()
except Exception as e:
    print e