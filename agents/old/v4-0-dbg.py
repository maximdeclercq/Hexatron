import numpy as np, random, time, pickle

def main():
    counter = 301

    with open("dumps/%d.dump" % counter, "rb") as dump:
        board, player_position, player_rotation, opponent_position, opponent_rotation = pickle.load(dump)

    print((board, player_position, player_rotation, opponent_position, opponent_rotation))

if __name__ == "__main__":
    main()
