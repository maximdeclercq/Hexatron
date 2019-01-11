from numpy import ndarray, array, array_equal
from time import time
from random import choice
from collections import deque

def rotation_to_position(rotation: int) -> ndarray:
    return array([(0, -1), (1, -1), (1, 0), (0, 1), (-1, 1), (-1, 0)][rotation % 6])

def calculate_new_state(position: ndarray, rotation: int, move: int = 0) -> ndarray:
    return position + rotation_to_position(rotation + move), (rotation + move) % 6

def is_playable(board: ndarray, position: ndarray) -> bool:
    return 0 <= position[0] < 13 and 0 <= position[1] < 13 and 6 <= position[0] + position[1] < 19 and not board[position[1], position[0]]

def calculate_distance_between(board: ndarray, position_a: ndarray, position_b: ndarray) -> int:
    new_board = board.copy()
    new_board[position_a[1], position_a[0]] = 1
    new_board[position_b[1], position_b[0]] = 0

    queue = deque([(position_a, 1)])
    while len(queue) > 0:
        position, distance = queue.popleft()

        if array_equal(position, position_b):
            return distance

        for i in range(-3, 3):
            new_position, _ = calculate_new_state(position, 0, i)

            if is_playable(new_board, new_position):
                queue.append((new_position, distance + 1))
                new_board[new_position[1], new_position[0]] = 1
    return None

def calculate_available_area(board: ndarray, position: ndarray) -> int:
    new_board = board.copy()
    
    count = 0
    queue = [position]
    while len(queue) > 0:
        position = queue.pop()

        for i in range(-3, 3):
            new_position, _ = calculate_new_state(position, i)

            if is_playable(new_board, new_position):
                queue.append(new_position)
                new_board[new_position[1], new_position[0]] = 1
                count += 1
    return count

def get_best_move_with_ray_casting(board: ndarray, player_position: ndarray, player_rotation: int, opponent_position: ndarray, opponent_rotation: int) -> int:
    player_playable_moves = [move for move in range(-2, 3) if is_playable(board, calculate_new_state(player_position, player_rotation, move)[0])]
    if player_playable_moves == []: return 0

    opponent_playable_moves = [move for move in range(-2, 3) if is_playable(board, calculate_new_state(opponent_position, opponent_rotation, move)[0])]
    if opponent_playable_moves == []: return player_playable_moves[0]

    ratings = []
    for player_move in player_playable_moves:
        new_player_position, new_player_rotation = calculate_new_state(player_position, player_rotation, player_move)

        player_minimal_area = 1e9
        opponent_maximal_area = 0

        for opponent_move in opponent_playable_moves:
            new_opponent_position, new_opponent_rotation = calculate_new_state(opponent_position, opponent_rotation, opponent_move)

            new_board = board.copy()
            new_board[new_player_position[1], new_player_position[0]] = 1
            new_board[new_opponent_position[1], new_opponent_position[0]] = 1

            player_ray_position = new_player_position.copy()
            player_ray_length = 1

            opponent_ray_position = new_opponent_position.copy()
            opponent_ray_length = 1

            while not array_equal(player_ray_position, opponent_ray_position):
                new_player_ray_position, new_player_rotation = calculate_new_state(player_ray_position, new_player_rotation)
                new_opponent_ray_position, new_opponent_rotation = calculate_new_state(opponent_ray_position, new_opponent_rotation)

                is_new_player_ray_position_playable = is_playable(new_board, new_player_ray_position)
                is_new_opponent_ray_position_playable = is_playable(new_board, new_opponent_ray_position)

                if not is_new_player_ray_position_playable and not is_new_opponent_ray_position_playable:
                    break
                
                if is_new_player_ray_position_playable:
                    player_ray_position = new_player_ray_position
                    player_ray_length += 1
                    new_board[player_ray_position[1], player_ray_position[0]] = 1

                if is_new_opponent_ray_position_playable:
                    opponent_ray_position = new_opponent_ray_position
                    opponent_ray_length += 1
                    new_board[opponent_ray_position[1], opponent_ray_position[0]] = 1
            
            player_partial_maximum_area = 0
            opponent_partial_maximum_area = 0
            previous_player_move = None
            previous_opponent_move = None
            for move in range(-2, 3):
                new_player_ray_position, _ = calculate_new_state(player_ray_position, new_player_rotation, move)
                new_opponent_ray_position, _ = calculate_new_state(opponent_ray_position, new_opponent_rotation, move)

                is_new_player_ray_position_playable = is_playable(new_board, new_player_ray_position)
                is_new_opponent_ray_position_playable = is_playable(new_board, new_opponent_ray_position)

                if is_new_player_ray_position_playable:
                    if previous_player_move is None or abs((move - previous_player_move) % 6) != 1:
                        player_partial_maximum_area = max(player_partial_maximum_area, calculate_available_area(new_board, new_player_ray_position)  / (2 if calculate_distance_between(new_board, new_player_ray_position, opponent_ray_position) is not None else 1))
                    previous_player_move = move

                if is_new_opponent_ray_position_playable:
                    if previous_opponent_move is None or abs((move - previous_opponent_move) % 6) != 1:
                        opponent_partial_maximum_area = max(opponent_partial_maximum_area, calculate_available_area(new_board, new_opponent_ray_position)  / (2 if calculate_distance_between(new_board, new_opponent_ray_position, player_ray_position) is not None else 1))
                    previous_opponent_move = move
            
            player_minimal_area = min(player_minimal_area, player_ray_length + player_partial_maximum_area)
            opponent_maximal_area = max(opponent_maximal_area, opponent_ray_length + opponent_partial_maximum_area)

        ratings += [(player_minimal_area / (opponent_maximal_area if opponent_maximal_area != 0 else 1e-9), player_move)]

    mx = max(ratings)[0]
    return choice([move for rating, move in ratings if abs(mx - rating) < 1e-9])

def generate_move(board: ndarray, positions: list, rotations: list) -> int:
    board = board.sum(axis=2)
    player_position, player_rotation = array(positions[0]), rotations[0]
    opponent_position, opponent_rotation = array(positions[1]), rotations[1]

    t0 = time()

    move = get_best_move_with_ray_casting(board, player_position, player_rotation, opponent_position, opponent_rotation)

    t = time() - t0
    assert t <= 1, "Exceeded execution time with %.3f seconds" % t

    return move
