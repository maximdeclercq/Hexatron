import numpy as np, random, time, pickle, os, hashlib

# This was meant to be a generator for version v40 but was canceled (this program should be run directly and not through the simulator)
# It's sole purpose is to simulate every possible game
# Please be careful since this bot will create a new folder 'dumps' and will flood it with game dumps because the required memory on a computer is too low to memorize every game
# This simulation could take years, even when optimized heavily, hence why this version was never used

def to_file_name(board, player_position, player_rotation, opponent_position, opponent_rotation):
    return ('dumps/'
        + hashlib.sha512(board).hexdigest()
        + str(player_position[0])
        + str(player_position[1])
        + str(player_rotation)
        + str(opponent_position[0])
        + str(opponent_position[1])
        + str(opponent_rotation)
        + '.dump')

def rotation_to_position(rotation: int) -> np.ndarray:
    return [np.array(rotation) for rotation in [(0, -1), (1, -1), (1, 0), (0, 1), (-1, 1), (-1, 0)]][rotation % 6]

def is_inside_bounds(position: np.ndarray) -> bool:
    return (0 <= position[0] < 13 and 0 <= position[1] < 13 and
            13 // 2 <= position[0] + position[1] < 13 * 3 // 2)

def is_occupied(board: np.ndarray, position: np.ndarray) -> bool:
    return board[position[1], position[0]]

def is_playable(board: np.ndarray, position: np.ndarray) -> bool:
    return is_inside_bounds(position) and not is_occupied(board, position)

def calculate_available_area(board: np.ndarray, position: np.ndarray) -> int:
    new_board = board.copy()
    
    count = 0
    queue = [position]
    while len(queue) > 0:
        position = queue.pop(0)

        for i in range(-3, 3):
            new_position = position + rotation_to_position(i)

            if is_playable(new_board, new_position):
                new_board[new_position[1], new_position[0]] = 1
                count += 1
                queue.append(new_position)
    return count

def calculate_new_position(player_position: np.ndarray, player_rotation: int, move: int) -> np.ndarray:
    return player_position + rotation_to_position(player_rotation + move)

def calculate_new_rotation(player_rotation: int, move: int) -> np.ndarray:
    return (player_rotation + move) % 6

def main():
    wins, draws, losses = 0, 0, 0

    empty_board = np.zeros((13, 13))
    possible_player_rotations = [1, 2]
    possible_opponent_rotations = [4, 5]
    possible_moves = [move for move in range(-2, 3)]
    counter = 0
    amount = 0

    for y in range(0, 4):
        for x in range(9, 13):
            player_position = np.array([x, y])
            opponent_position = np.array([13 - x, 13 - y])
            for player_rotation in possible_player_rotations:
                for opponent_rotation in possible_opponent_rotations:
                    board = empty_board.copy()

                    with open(to_file_name(board, player_position, player_rotation, opponent_position, opponent_rotation), "wb") as dump:
                        pickle.dump([board, player_position, player_rotation, opponent_position, opponent_rotation, 0], dump)
                        amount += 1
                    while len(os.listdir('dumps')) > 0:
                        file_name = os.listdir('dumps')[0]
                        with open('dumps/' + file_name, 'rb') as dump:
                            board, player_position, player_rotation, opponent_position, opponent_rotation, moves = pickle.load(dump)
                        os.remove('dumps/' + file_name)

                        new_player_states = []
                        new_opponent_states = []
                        for move in possible_moves:
                            new_player_position = calculate_new_position(player_position, player_rotation, move)
                            new_player_rotation = calculate_new_rotation(player_rotation, move)
                            new_opponent_position = calculate_new_position(opponent_position, opponent_rotation, move)
                            new_opponent_rotation = calculate_new_rotation(opponent_rotation, move)

                            if is_playable(board, new_player_position):
                                new_player_states.append((new_player_position, new_player_rotation))
                            if is_playable(board, new_opponent_position):
                                new_opponent_states.append((new_opponent_position, new_opponent_rotation))

                        if new_player_states == [] and new_opponent_states == []:
                            draws += 1
                            counter += 1
                            print("DRAW")
                            print("%d / %d / %d (%d / %d) (%d)" % (wins, draws, losses, counter, amount, moves))
                            continue
                        elif new_player_states == []:
                            losses += 1
                            counter += 1
                            print("LOSS")
                            print("%d / %d / %d (%d / %d) (%d)" % (wins, draws, losses, counter, amount, moves))
                            continue
                        elif new_opponent_states == []:
                            wins += 1
                            counter += 1
                            print("WIN")
                            print("%d / %d / %d (%d / %d) (%d)" % (wins, draws, losses, counter, amount, moves))
                            continue

                        for opponent_state in new_opponent_states:
                            new_opponent_position, new_opponent_rotation = opponent_state

                            for player_state in new_player_states:
                                new_board = board.copy()

                                new_player_position, new_player_rotation = player_state

                                if new_player_position[0] == new_opponent_position[0] and new_player_position[1] == new_opponent_position[1]:
                                    draws += 1
                                    continue

                                new_board[new_player_position[1], new_player_position[0]] = 1
                                new_board[new_opponent_position[1], new_opponent_position[0]] = 1

                                with open(to_file_name(new_board, new_player_position, new_player_rotation, new_opponent_position, new_opponent_rotation), "wb") as dump:
                                    pickle.dump([new_board, new_player_position, new_player_rotation, new_opponent_position, new_opponent_rotation, moves + 1], dump)
                                    amount += 1
                        counter += 1
                        print("%d / %d / %d (%d / %d) (%d)" % (wins, draws, losses, counter, amount, moves))

if __name__ == "__main__":
    main()
