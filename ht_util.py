def ask_for_confirmation():
    answer = raw_input("Is this ok? [yes/no]: ")

    if answer != "yes":
        print "exit due to user quit"
        exit()



