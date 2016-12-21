def ask_for_confirmation():
    answer = input("Is this ok? [yes/no]: ")

    if answer != "yes":
        print("exit due to user quit")
        exit()

