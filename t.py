import datetime

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

print now



def two_return_test():
    a = 1
    b = 2
    return a,b

c, d = two_return_test()
print c, d