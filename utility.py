import random as rngesus

def roll(d=1, n=6):
    roll_list = []
    for _ in range(d):
        roll_list.append(rngesus.randint(1, n))
    return roll_list


if __name__ == "__main__":
    pass