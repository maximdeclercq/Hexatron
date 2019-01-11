import numpy as np, random

def get_rotations():
    #                                             NW       NE       E       SE       SW       W
    return [np.array(rotation) for rotation in [(0, -1), (1, -1), (1, 0), (0, 1), (-1, 1), (-1, 0)]]

def rotation_to_position(rotation: int):
    return get_rotations()[rotation % 6]
    
def position_to_rotation(position: np.ndarray):
    return [position[0] == rotation[0] and position[1] == rotation[1] for rotation in get_rotations()].index(True)

def is_inside_bounds(position: np.ndarray):
    return (0 <= position[0] < 13 and 0 <= position[1] < 13 and
            13 // 2 <= position[0] + position[1] < 13 * 3 // 2)

def is_occupied(board: np.ndarray, position: np.ndarray):
    return board[position[1], position[0]]

def flood_fill(board: np.ndarray, position: dict):
    distances = np.full((13, 13), -1)

    count = 0

    distances[position[0], position[1]] = 0
    queue = [position]
    while len(queue) > 0:
        position = queue.pop(0)

        for i in range(-3, 3):
            new_position = position + rotation_to_position(i)

            if is_inside_bounds(new_position) and not is_occupied(board, new_position):
                board[new_position[1], new_position[0]] = 1
                count += 1
                distances[new_position[0], new_position[1]] = distances[position[0], position[1]] + 1
                queue.append(new_position)
    return count

def dist(board: np.ndarray, position: np.ndarray, opponent: dict):
    distances = np.full((13, 13), -1)

    distances[opponent["position"][0], opponent["position"][1]] = 0
    queue = [(opponent["position"], opponent["orientation"])]
    while len(queue) > 0:
        position, orientation = queue.pop(0)

        for i in range(-2, 3):
            new_orientation = (orientation + i) % 6
            new_position = position + rotation_to_position(new_orientation)

            if position[0] == new_position[0] and position[1] == new_position[1]:
                return distances[position[0], position[1]] + 1
            if is_inside_bounds(new_position) and not is_occupied(board, new_position) and distances[new_position[0], new_position[1]] == -1:
                distances[new_position[0], new_position[1]] = distances[position[0], position[1]] + 1
                queue.append((new_position, new_orientation))
    return -1

def bfs(board: np.ndarray, player: dict, opponent: dict):
    targets = []
    for i in range(-2, 3):
        new_position = player["position"] + rotation_to_position(player["orientation"] + i)
        if is_inside_bounds(new_position) and not is_occupied(board, new_position):
            new_position = player["position"] + rotation_to_position(player["orientation"] + i
            targets += [(flood_fill(board, new_position)) if dist(board, new_position, opponent) > 2 else 0, i, new_position)]
    if len(targets) == 0:
        return [], []

    maximum = max(targets)[0]
    targets = [target[1:] for target in targets if target[0] == maximum]

    distances = np.full((13, 13), -1)

    distances[opponent["position"][0], opponent["position"][1]] = 0
    queue = [(opponent["position"], opponent["orientation"])]
    while len(queue) > 0:
        position, orientation = queue.pop(0)

        for i in range(-2, 3):
            new_orientation = (orientation + i) % 6
            new_position = position + rotation_to_position(new_orientation)

            if is_inside_bounds(new_position) and not is_occupied(board, new_position) and distances[new_position[0], new_position[1]] == -1:
                distances[new_position[0], new_position[1]] = distances[position[0], position[1]] + 1
                queue.append((new_position, new_orientation))
    return targets, distances

def get_best_move(board: np.ndarray, player: dict, opponent: dict):
    targets, distances = bfs(board, player, opponent)
    if len(targets) == 0:
        return 0
    maximum = max([distances[target[0], target[1]] for rotation, target in targets])
    return random.choice([rotation for rotation, target in targets if distances[target[0], target[1]] == maximum])

def generate_move(board: np.ndarray, positions: list, orientations: list):
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
    board = np.sum(board, axis=2)
    player = {"position": np.array(positions[0]), "orientation": orientations[0]}
    opponent = {"position": np.array(positions[1]), "orientation": orientations[1]}

    move = get_best_move(board, player, opponent)
    return move
