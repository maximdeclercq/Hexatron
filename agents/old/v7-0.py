from numpy import ndarray, array, array_equal
from time import time
from random import choice, seed
from collections import deque

def rotation_to_position(rotation: int) -> ndarray:
    return array([(0, -1), (1, -1), (1, 0), (0, 1), (-1, 1), (-1, 0)][rotation % 6])

def calculate_new_state(position: ndarray, rotation: int, move: int = 0) -> ndarray:
    return position + rotation_to_position(rotation + move), (rotation + move) % 6

def is_allowed(board: ndarray, position: ndarray) -> bool:
    return 0 <= position[0] < 13 and 0 <= position[1] < 13 and 6 <= position[0] + position[1] < 19

def is_playable(board: ndarray, position: ndarray) -> bool:
    return is_allowed(board, position) and not board[position[1], position[0], 0] and not board[position[1], position[0], 1]

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

def get_best_move_with_ray_casting(board: ndarray, player_position: ndarray, player_rotation: int, opponent_position: ndarray, opponent_rotation: int, player_playable_moves: list = None) -> int:
    if player_playable_moves is None:
        player_playable_moves = [move for move in range(-2, 3) if is_playable(board, calculate_new_state(player_position, player_rotation, move)[0])]
        if player_playable_moves == []: return 0
    
    hit_max = []

    for move in player_playable_moves:
        new_board = board.copy()
        position, _ = calculate_new_state(player_position, player_rotation, move)
        difference = position - player_position
            
        distance_to_opponent = calculate_distance_between(new_board, position, opponent_position)
        best_area_with_opponent = calculate_available_area(new_board, opponent_position)
        best_area_without_opponent = 0

        ray_position = player_position + difference
        new_board[ray_position[1], ray_position[0]] = 1
        distance_from_ray_to_player = 1
        while is_playable(new_board, ray_position + difference):
            ray_position += difference
            distance_from_ray_to_player += 1
            new_board[ray_position[1], ray_position[0]] = 1

        distance_from_ray_to_opponent = calculate_distance_between(new_board, ray_position, opponent_position)
        if distance_from_ray_to_opponent is not None:
            best_area_with_opponent += (distance_from_ray_to_player > distance_from_ray_to_opponent) / 32
        if distance_to_opponent is not None:
            best_area_with_opponent -= distance_to_opponent / 128

        for new_move in range(-2, 3):
            new_ray_position, _ = calculate_new_state(ray_position, player_rotation + move, new_move)
            if is_playable(new_board, new_ray_position):
                distance_to_opponent = calculate_distance_between(new_board, new_ray_position, opponent_position)

                if distance_to_opponent is None:
                    best_area_without_opponent = max(best_area_without_opponent, calculate_available_area(new_board, new_ray_position))
                else:
                    best_area_without_opponent = max(best_area_without_opponent, calculate_available_area(new_board, new_ray_position) // 2)
        hit_max += [(best_area_without_opponent / (best_area_with_opponent if best_area_with_opponent != 0 else 1e-3), move)]
    mx = max(hit_max)
    #print(hit_max)
    return choice([hit for hit in hit_max if abs(mx[0] - hit[0]) < 1e-9])[1]

def get_best_move_with_flooding(board: ndarray, player_position: ndarray, player_rotation: int, opponent_position: ndarray, opponent_rotation: int) -> int:
    player_playable_moves = [move for move in range(-2, 3) if is_playable(board, calculate_new_state(player_position, player_rotation, move)[0])]
    if player_playable_moves == []: return 0

    opponent_playable_moves = [move for move in range(-2, 3) if is_playable(board, calculate_new_state(opponent_position, opponent_rotation, move)[0])]
    if len(player_playable_moves) == 1 or opponent_playable_moves == []: return player_playable_moves[0]

    ratings = []
    for player_move in player_playable_moves:
        new_player_position, new_player_rotation = calculate_new_state(player_position, player_rotation, player_move)

        player_minimal_area = 1e9
        opponent_maximal_area = 0

        for opponent_move in opponent_playable_moves:
            new_opponent_position, new_opponent_rotation = calculate_new_state(opponent_position, opponent_rotation, opponent_move)

            player_area = 0
            opponent_area = 0

            new_board = board.copy()
            new_board[new_player_position[1], new_player_position[0], 0] = -1
            new_board[new_opponent_position[1], new_opponent_position[0], 1] = -1

            move = -2
            queue = deque([(0, new_player_position, move), (1, new_opponent_position, move)])
            while len(queue) > 0:
                player, position, move = queue.popleft()

                for i in range(-3, 3):
                    new_position, _ = calculate_new_state(position, i)

                    if is_playable(new_board, new_position):
                        if player == 0:
                            player_area += 1
                        else:
                            opponent_area += 1
                        new_board[new_position[1], new_position[0], player] = move
                        queue.append((player, new_position, move - 1))
                    elif is_allowed(new_board, new_position) and new_board[new_position[1], new_position[0], 1 - player] == move:
                        if player == 0:
                            player_area += 0.5
                            opponent_area -= 0.5
                        else:
                            opponent_area += 0.5
                            player_area -= 0.5
            
            if opponent_area > opponent_maximal_area:
                opponent_maximal_area = opponent_area
                player_minimal_area = player_area
            elif opponent_area == opponent_maximal_area:
                player_minimal_area = min(player_minimal_area, player_area)
        
        ratings += [(player_minimal_area / (opponent_maximal_area if opponent_maximal_area != 0 else 1e-9), player_move)]
    
    mx = max(ratings)[0]
    return choice([move for rating, move in ratings if abs(mx - rating) < 1e-9])

def generate_move(board: ndarray, positions: list, rotations: list) -> int:
    player_position, player_rotation = array(positions[0]), rotations[0]
    opponent_position, opponent_rotation = array(positions[1]), rotations[1]

    t0 = time()

    if calculate_distance_between(board, player_position, opponent_position) is not None:
        move = get_best_move_with_flooding(board, player_position, player_rotation, opponent_position, opponent_rotation)
    else:
        move = get_best_move_with_ray_casting(board, player_position, player_rotation, opponent_position, opponent_rotation)

    t = time() - t0
    assert t <= 1, "Exceeded execution time with %.3f seconds" % t

    return move
