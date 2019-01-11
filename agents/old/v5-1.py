import numpy as np, random, time

def rotation_to_position(rotation: int) -> np.ndarray:
    return [np.array(rotation) for rotation in [(0, -1), (1, -1), (1, 0), (0, 1), (-1, 1), (-1, 0)]][rotation % 6]

def calculate_new_position(position: np.ndarray, rotation: int, move: int) -> np.ndarray:
    return position + rotation_to_position(rotation + move)

def is_inside_bounds(position: np.ndarray) -> bool:
    return (0 <= position[0] < 13 and 0 <= position[1] < 13 and
            13 // 2 <= position[0] + position[1] < 13 * 3 // 2)

def is_occupied(board: np.ndarray, position: np.ndarray) -> bool:
    return board[position[1], position[0]]

def is_playable(board: np.ndarray, position: np.ndarray) -> bool:
    return is_inside_bounds(position) and not is_occupied(board, position)

def calculate_distance_between(board: np.ndarray, position_a: np.ndarray, position_b: np.ndarray) -> int:
    if position_a[0] == position_b[0] and position_a[1] == position_b[1]:
        return 0
	
    new_board = board.copy()

    queue = [(position_b, 1)]
    while len(queue) > 0:
        position, distance = queue.pop(0)

        for i in range(-3, 3):
            new_position = position + rotation_to_position(i)

            if position_a[0] == new_position[0] and position_a[1] == new_position[1]:
                return distance
            if is_playable(new_board, new_position):
                new_board[new_position[1], new_position[0]] = 1
                queue.append((new_position, distance + 1))
    return 1e9

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

def get_best_move_with_targeting(board: np.ndarray, player_position: np.ndarray, player_rotation: int, opponent_position: np.ndarray, opponent_rotation: int, target: np.ndarray) -> int:
    print("Targeting (%d, %d)" % (target[0], target[1]))
    distances = []
    for move in range(-2, 3):
        new_position = calculate_new_position(player_position, player_rotation, move)
        if is_playable(board, new_position):
            distance = calculate_distance_between(board, new_position, target)  
            distances.append((distance, move))
    return min(distances)[1]

def get_best_move_with_ray_casting(board: np.ndarray, player_position: np.ndarray, player_rotation: int, opponent_position: np.ndarray, opponent_rotation: int, playable_moves: list) -> int:
    print("Casting rays from (%d, %d)" % (player_position[0], player_position[1]))

    hit_max = []
    for move in playable_moves:
        new_board = board.copy()
        position = calculate_new_position(player_position, player_rotation, move)
        difference = position - player_position
        ray_position = player_position + difference
        ray_length = 1
        while is_playable(new_board, ray_position + difference):
            ray_position += difference
            ray_length += 1
            new_board[ray_position[1], ray_position[0]] = 1
            
        best_area_with_opponent = 0
        best_area_without_opponent = 0
        for new_move in range(-2, 3):
            new_ray_position = calculate_new_position(ray_position, player_rotation + move, new_move)
            if is_playable(new_board, new_ray_position):
                distance_to_opponent = calculate_distance_between(new_board, new_ray_position, opponent_position)

                print(move, new_move, distance_to_opponent, ray_length, calculate_available_area(new_board, new_ray_position))

                if ray_length <= distance_to_opponent < 1e9:
                    best_area_with_opponent += 2 * calculate_available_area(new_board, new_ray_position)
                elif distance_to_opponent < 1e9:
                    best_area_with_opponent += calculate_available_area(new_board, new_ray_position)
                else:
                    best_area_without_opponent += calculate_available_area(new_board, new_ray_position)
        hit_max += [(best_area_without_opponent / (best_area_with_opponent if best_area_with_opponent != 0 else 1e-9), move)]

    print(hit_max)
    return max(hit_max)[1]

def get_best_move_with_floodfill(board: np.ndarray, player_position: np.ndarray, player_rotation: int, opponent_position: np.ndarray, opponent_rotation: int) -> int:
    print("Finding the best area with floodfill") 
    playable_areas = [(calculate_available_area(board, calculate_new_position(player_position, player_rotation, j)), j) for j in range(-2, 3) if is_playable(board, calculate_new_position(player_position, player_rotation, j))]
    return max(playable_areas)[1]

def get_best_move(board: np.ndarray, player_position: np.ndarray, player_rotation: int, opponent_position: np.ndarray, opponent_rotation: int) -> int:
    playable_moves = [move for move in range(-2, 3) if is_playable(board, calculate_new_position(player_position, player_rotation, move))]
    if playable_moves == []: return 0

    playable_positions = [(calculate_new_position(player_position, player_rotation, move), move) for move in playable_moves]
    playable_areas = [(calculate_available_area(board, position), move) for position, move in playable_positions]

    if len(set([area for area, move in playable_areas])) == 1:    
        distance_to_opponent = calculate_distance_between(board, player_position, opponent_position)
        distance_to_middle = calculate_distance_between(board, player_position, np.array([6, 6]))
        distance_from_middle_to_opponent = calculate_distance_between(board, np.array([6, 6]), opponent_position)

        if not board[6, 6] and 2 <= distance_from_middle_to_opponent < 1e9 and 0 <= distance_to_middle < 1e9:
            return get_best_move_with_targeting(board, player_position, player_rotation, opponent_position, opponent_rotation, np.array([6, 6]))
        elif distance_to_opponent < 1e9:
            return get_best_move_with_ray_casting(board, player_position, player_rotation, opponent_position, opponent_rotation, playable_moves)
        else:
            print("Filling area")
            return playable_moves[-1]
    return get_best_move_with_floodfill(board, player_position, player_rotation, opponent_position, opponent_rotation)

def generate_move(board: np.ndarray, positions: list, rotations: list) -> int:
    board = board.sum(axis=2)
    player_position, player_rotation = np.array(positions[0]), rotations[0]
    opponent_position, opponent_rotation = np.array(positions[1]), rotations[1]

    t0 = time.time()
    
    move = get_best_move(board, player_position, player_rotation, opponent_position, opponent_rotation)

    t = time.time() - t0
    assert t <= 1, "Exceeded execution time with %.3f seconds" % t

    return move
