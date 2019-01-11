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

def get_best_move(board: np.ndarray, player: object, opponent: object) -> int:
    t0 = time.time()

    amount_of_wins_and_losses = [[calculate_available_area(board, player.position + rotation_to_position(player.rotation + i)) // 10, 0] for i in range(-2, 3)]

    time_left = 1 - (time.time() - t0)

    for i in range(-2, 3):
        t0 = time.time()
        while time.time() - t0 < 0.2 * 0.95 * time_left:
            new_board = board.copy()
            new_player = type("", (), {"position": player.position.copy(), "rotation": player.rotation})()
            new_opponent = type("", (), {"position": opponent.position.copy(), "rotation": opponent.rotation})()
            first = True
            while True:
                player_targets, opponent_targets = [], []
                for j in range(-2, 3):
                    new_player_position = new_player.position + rotation_to_position(new_player.rotation + (i if first else j))
                    new_opponent_position = new_opponent.position + rotation_to_position(new_opponent.rotation + j)
                    
                    if is_playable(new_board, new_player_position) and (new_player_position[0] != new_opponent_position[0] or new_player_position[1] != new_opponent_position[1]):
                        player_targets += [(new_player_position, i if first else j)]
                    if is_playable(new_board, new_opponent_position) and (new_player_position[0] != new_opponent_position[0] or new_player_position[1] != new_opponent_position[1]):
                        opponent_targets += [(new_opponent_position, j)]
                if player_targets == [] and opponent_targets == []:
                    break
                elif player_targets == []:
                    amount_of_wins_and_losses[i][1] += 1
                    break
                elif opponent_targets == []:
                    amount_of_wins_and_losses[i][0] += 1
                    break
                new_player.position, new_player.rotation = random.choice(player_targets)
                new_opponent.position, new_opponent.rotation = random.choice(opponent_targets)
                new_board[new_player.position[1], new_player.position[0], 0] = 1
                new_board[new_opponent.position[1], new_opponent.position[0], 1] = 1
                first = False

    win_lose_ratios = [wins / (losses if losses > 0 else 0.1) for wins, losses in amount_of_wins_and_losses]
    mx = max(win_lose_ratios)
    if all(win_lose_ratio == mx for win_lose_ratio in win_lose_ratios):
        moves = [move for move in range(-2, 3) if is_playable(board, player.position + rotation_to_position(player.rotation + move))]
        if len(moves) == 0:
            return 0
        return random.choice(moves)
    best_moves = [move for move in range(-2, 3) if win_lose_ratios[move] == mx]
    return random.choice(best_moves)

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

    move = get_best_move(board, player, opponent)
    return move
