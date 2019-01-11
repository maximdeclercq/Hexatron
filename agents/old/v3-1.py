import numpy as np, random, time

def rotation_to_position(rotation: int) -> np.ndarray:
    return [np.array(rotation) for rotation in [(0, -1), (1, -1), (1, 0), (0, 1), (-1, 1), (-1, 0)]][rotation % 6]

def is_inside_bounds(position: np.ndarray) -> bool:
    return (0 <= position[0] < 13 and 0 <= position[1] < 13 and
            13 // 2 <= position[0] + position[1] < 13 * 3 // 2)

def is_occupied_by_player(board: np.ndarray, position: np.ndarray) -> bool:
    return board[position[1], position[0], 0]

def is_occupied_by_opponent(board: np.ndarray, position: np.ndarray) -> bool:
    return board[position[1], position[0], 1]

def is_occupied(board: np.ndarray, position: np.ndarray) -> bool:
    return is_occupied_by_player(board, position) or is_occupied_by_opponent(board, position)

def is_playable(board: np.ndarray, position: np.ndarray) -> bool:
    return is_inside_bounds(position) and not is_occupied(board, position)

def calculate_distance_between(board: np.ndarray, position_a: np.ndarray, position_b: np.ndarray) -> int:
    new_board = board.copy()

    queue = [(position_b, 0)]
    while len(queue) > 0:
        position, distance = queue.pop(0)

        for i in range(-3, 3):
            new_position = position + rotation_to_position(i)

            if position_a[0] == new_position[0] and position_a[1] == new_position[1]:
                return distance
            if is_playable(new_board, new_position):
                new_board[new_position[1], new_position[0]] = 1
                queue.append((new_position, distance + 1))
    return -1

def calculate_available_area(board: np.ndarray, position: np.ndarray) -> int:
    new_board = board.copy()
    
    count = 0
    queue = [position]
    while len(queue) > 0:
        position = queue.pop(0)

        for i in range(-3, 3):
            new_position = position + rotation_to_position(i)

            if is_playable(new_board, new_position):
                new_board[new_position[1], new_position[0], 0] = 1
                count += 1
                queue.append(new_position)
    return count

def calculate_win_probability(board: np.ndarray, player: object, opponent: object, move: int, max_time: int) -> float:
    wins, losses = 0, 0

    t0 = time.time()
    while time.time() - t0 < 0.75 * max_time:
        new_board = board.copy()
        new_player = type("", (), {"position": player.position.copy(), "rotation": player.rotation})()
        new_opponent = type("", (), {"position": opponent.position.copy(), "rotation": opponent.rotation})()
        first = True
        while True:
            player_targets, opponent_targets = [], []
            for j in range(-2, 3):
                new_player_position = new_player.position + rotation_to_position(new_player.rotation + (move if first else j))
                new_opponent_position = new_opponent.position + rotation_to_position(new_opponent.rotation + j)
                
                if is_playable(new_board, new_player_position) and (new_player_position[0] != new_opponent_position[0] or new_player_position[1] != new_opponent_position[1]):
                    player_targets += [(new_player_position, move if first else j)]
                if is_playable(new_board, new_opponent_position) and (new_player_position[0] != new_opponent_position[0] or new_player_position[1] != new_opponent_position[1]):
                    opponent_targets += [(new_opponent_position, j)]
            if player_targets == [] and opponent_targets == []:
                losses += 2
                break
            elif player_targets == []:
                losses += 3
                break
            elif opponent_targets == []:
                wins += 4
                break
            new_player.position, new_player.rotation = random.choice(player_targets)
            new_opponent.position, new_opponent.rotation = random.choice(opponent_targets)
            new_board[new_player.position[1], new_player.position[0], 0] = 1
            new_board[new_opponent.position[1], new_opponent.position[0], 1] = 1
            first = False
    return wins / (losses if losses > 0 else 1e-9)

def get_best_move(board: np.ndarray, player: object, opponent: object) -> int:
    t0 = time.time()

    playable_moves = [(calculate_available_area(board, player.position + rotation_to_position(player.rotation + move)), move) for move in range(-2, 3) if is_playable(board, player.position + rotation_to_position(player.rotation + move))]
    if not len(playable_moves):
        return 0

    playable_areas = [area for area, move in playable_moves]
    unique_areas = set(playable_areas)

    if len(unique_areas) == 1 and calculate_distance_between(board, player.position, opponent.position) >= 0:
        # move with best chance to win
        time_left = 1 - (time.time() - t0)
        win_probabilities = [(calculate_win_probability(board, player, opponent, move, time_left / len(playable_moves)), move) for _, move in playable_moves]
        mx, _ = max(win_probabilities)
        best_moves = [move for win_probability, move in win_probabilities if win_probability == mx]
        return random.choice(best_moves)
    elif len(unique_areas) > 1:
        # best area
        mx, _ = max(playable_moves)
        best_moves = [move for area, move in playable_moves if area == mx]
        other_moves = [move for area, move in playable_moves if area != mx]
        for move in best_moves:
            new_position = player.position + rotation_to_position(player.rotation + move)
            if calculate_distance_between(board, new_position, opponent.position) < 0:
                return move
        time_left = 1 - (time.time() - t0)
        best_win_probabilities = [(calculate_win_probability(board, player, opponent, move, time_left / len(playable_moves)), move) for move in best_moves]
        best_win_probabilities = [(win_probability, move) for win_probability, move in best_win_probabilities if win_probability > 1]
        other_win_probabilities = [(calculate_win_probability(board, player, opponent, move, time_left / len(playable_moves)), move) for move in other_moves]
        other_win_probabilities = [(win_probability, move) for win_probability, move in other_win_probabilities if win_probability > 1]
        if len(best_win_probabilities):
            return sorted(best_win_probabilities, reverse=True)[0][1]
        elif len(other_win_probabilities):
            return sorted(other_win_probabilities, reverse=True)[0][1]
        return random.choice(best_moves)
    else:
        # fill area
        return playable_moves[-1][1]

def generate_move(board: np.ndarray, positions: list, rotations: list) -> int:
    """generates a move
    arguments:
        board: a 3D array, representing the playing field. The array has a shape of (13, 13, 2). The first two dimensions are Y-
            and X-axis. The third dimension contains the trail of each agent. More specific, at the start of the game,
            board[:, :, 0] will contain a single 1, at the Y -and X-coordinate of your agent. Similarly, board[:, :, 1] will
            contain a 1 at your opponent's location. As the game advances, more cells will contain 1's, indicating longer trails.
        positions: a list, containing two tuples. The first tuple (x, y) encodes the position of your agent, while the second tuple
            encodes your opponent's position.
        orientations: similar to positions, a list containing two orientations (integers in [0,5]), both for your agent and your
            opponent. The orientation is encoded as the index of the compass point in ['NW', 'NE', 'E', 'SE', 'SW', 'W'].
    returns:
        move: an integer in [-2,2], representing one of the possible rotations (120° counterclockwise, 60° counterclockwise, 0°,
            60° clockwise, 120° clockwise), before moving forward.
    """
    player = type("", (), {"position": np.array(positions[0]), "rotation": rotations[0]})()
    opponent =  type("", (), {"position": np.array(positions[1]), "rotation": rotations[1]})()

    t0 = time.time()
    
    move = get_best_move(board, player, opponent)

    t = time.time() - t0
    assert t <= 1, "Exceeded execution time with %.3f seconds" % t
    
    return move
