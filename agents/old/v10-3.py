from numpy import ndarray, array, array_equal, zeros, where, append
from time import time
from random import choice
from collections import namedtuple, deque

def get_nodes():
    return {(6, 0): 0, (7, 0): 1, (8, 0): 2, (9, 0): 3, (10, 0): 4, (11, 0): 5, (12, 0): 6, (5, 1): 7, (6, 1): 8, (7, 1): 9, (8, 1): 10, (9, 1): 11, (10, 1): 12, (11, 1): 13, (12, 1): 14, (4, 2): 15, (5, 2): 16, (6, 2): 17, (7, 2): 18, (8, 2): 19, (9, 2): 20, (10, 2): 21, (11, 2): 22, (12, 2): 23, (3, 3): 24, (4, 3): 25, (5, 3): 26, (6, 3): 27, (7, 3): 28, (8, 3): 29, (9, 3): 30, (10, 3): 31, (11, 3): 32, (12, 3): 33, (2, 4): 34, (3, 4): 35, (4, 4): 36, (5, 4): 37, (6, 4): 38, (7, 4): 39, (8, 4): 40, (9, 4): 41, (10, 4): 42, (11, 4): 43, (12, 4): 44, (1, 5): 45, (2, 5): 46, (3, 5): 47, (4, 5): 48, (5, 5): 49, (6, 5): 50, (7, 5): 51, (8, 5): 52, (9, 5): 53, (10, 5): 54, (11, 5): 55, (12, 5): 56, (0, 6): 57, (1, 6): 58, (2, 6): 59, (3, 6): 60, (4, 6): 61, (5, 6): 62, (6, 6): 63, (7, 6): 64, (8, 6): 65, (9, 6): 66, (10, 6): 67, (11, 6): 68, (12, 6): 69, (0, 7): 70, (1, 7): 71, (2, 7): 72, (3, 7): 73, (4, 7): 74, (5, 7): 75, (6, 7): 76, (7, 7): 77, (8, 7): 78, (9, 7): 79, (10, 7): 80, (11, 7): 81, (0, 8): 82, (1, 8): 83, (2, 8): 84, (3, 8): 85, (4, 8): 86, (5, 8): 87, (6, 8): 88, (7, 8): 89, (8, 8): 90, (9, 8): 91, (10, 8): 92, (0, 9): 93, (1, 9): 94, (2, 9): 95, (3, 9): 96, (4, 9): 97, (5, 9): 98, (6, 9): 99, (7, 9): 100, (8, 9): 101, (9, 9): 102, (0, 10): 103, (1, 10): 104, (2, 10): 105, (3, 10): 106, (4, 10): 107, (5, 10): 108, (6, 10): 109, (7, 10): 110, (8, 10): 111, (0, 11): 112, (1, 11): 113, (2, 11): 114, (3, 11): 115, (4, 11): 116, (5, 11): 117, (6, 11): 118, (7, 11): 119, (0, 12): 120, (1, 12): 121, (2, 12): 122, (3, 12): 123, (4, 12): 124, (5, 12): 125, (6, 12): 126}

def get_node(position):
    return get_nodes()[tuple(position)]

def get_next_nodes():
    return [[None, None, 1, 8, 7, None], [None, None, 2, 9, 8, 0], [None, None, 3, 10, 9, 1], [None, None, 4, 11, 10, 2], [None, None, 5, 12, 11, 3], [None, None, 6, 13, 12, 4], [None, None, None, 14, 13, 5], [None, 0, 8, 16, 15, None], [0, 1, 9, 17, 16, 7], [1, 2, 10, 18, 17, 8], [2, 3, 11, 19, 18, 9], [3, 4, 12, 20, 19, 10], [4, 5, 13, 21, 20, 11], [5, 6, 14, 22, 21, 12], [6, None, None, 23, 22, 13], [None, 7, 16, 25, 24, None], [7, 8, 17, 26, 25, 15], [8, 9, 18, 27, 26, 16], [9, 10, 19, 28, 27, 17], [10, 11, 20, 29, 28, 18], [11, 12, 21, 30, 29, 19], [12, 13, 22, 31, 30, 20], [13, 14, 23, 32, 31, 21], [14, None, None, 33, 32, 22], [None, 15, 25, 35, 34, None], [15, 16, 26, 36, 35, 24], [16, 17, 27, 37, 36, 25], [17, 18, 28, 38, 37, 26], [18, 19, 29, 39, 38, 27], [19, 20, 30, 40, 39, 28], [20, 21, 31, 41, 40, 29], [21, 22, 32, 42, 41, 30], [22, 23, 33, 43, 42, 31], [23, None, None, 44, 43, 32], [None, 24, 35, 46, 45, None], [24, 25, 36, 47, 46, 34], [25, 26, 37, 48, 47, 35], [26, 27, 38, 49, 48, 36], [27, 28, 39, 50, 49, 37], [28, 29, 40, 51, 50, 38], [29, 30, 41, 52, 51, 39], [30, 31, 42, 53, 52, 40], [31, 32, 43, 54, 53, 41], [32, 33, 44, 55, 54, 42], [33, None, None, 56, 55, 43], [None, 34, 46, 58, 57, None], [34, 35, 47, 59, 58, 45], [35, 36, 48, 60, 59, 46], [36, 37, 49, 61, 60, 47], [37, 38, 50, 62, 61, 48], [38, 39, 51, 63, 62, 49], [39, 40, 52, 64, 63, 50], [40, 41, 53, 65, 64, 51], [41, 42, 54, 66, 65, 52], [42, 43, 55, 67, 66, 53], [43, 44, 56, 68, 67, 54], [44, None, None, 69, 68, 55], [None, 45, 58, 70, None, None], [45, 46, 59, 71, 70, 57], [46, 47, 60, 72, 71, 58], [47, 48, 61, 73, 72, 59], [48, 49, 62, 74, 73, 60], [49, 50, 63, 75, 74, 61], [50, 51, 64, 76, 75, 62], [51, 52, 65, 77, 76, 63], [52, 53, 66, 78, 77, 64], [53, 54, 67, 79, 78, 65], [54, 55, 68, 80, 79, 66], [55, 56, 69, 81, 80, 67], [56, None, None, None, 81, 68], [57, 58, 71, 82, None, None], [58, 59, 72, 83, 82, 70], [59, 60, 73, 84, 83, 71], [60, 61, 74, 85, 84, 72], [61, 62, 75, 86, 85, 73], [62, 63, 76, 87, 86, 74], [63, 64, 77, 88, 87, 75], [64, 65, 78, 89, 88, 76], [65, 66, 79, 90, 89, 77], [66, 67, 80, 91, 90, 78], [67, 68, 81, 92, 91, 79], [68, 69, None, None, 92, 80], [70, 71, 83, 93, None, None], [71, 72, 84, 94, 93, 82], [72, 73, 85, 95, 94, 83], [73, 74, 86, 96, 95, 84], [74, 75, 87, 97, 96, 85], [75, 76, 88, 98, 97, 86], [76, 77, 89, 99, 98, 87], [77, 78, 90, 100, 99, 88], [78, 79, 91, 101, 100, 89], [79, 80, 92, 102, 101, 90], [80, 81, None, None, 102, 91], [82, 83, 94, 103, None, None], [83, 84, 95, 104, 103, 93], [84, 85, 96, 105, 104, 94], [85, 86, 97, 106, 105, 95], [86, 87, 98, 107, 106, 96], [87, 88, 99, 108, 107, 97], [88, 89, 100, 109, 108, 98], [89, 90, 101, 110, 109, 99], [90, 91, 102, 111, 110, 100], [91, 92, None, None, 111, 101], [93, 94, 104, 112, None, None], [94, 95, 105, 113, 112, 103], [95, 96, 106, 114, 113, 104], [96, 97, 107, 115, 114, 105], [97, 98, 108, 116, 115, 106], [98, 99, 109, 117, 116, 107], [99, 100, 110, 118, 117, 108], [100, 101, 111, 119, 118, 109], [101, 102, None, None, 119, 110], [103, 104, 113, 120, None, None], [104, 105, 114, 121, 120, 112], [105, 106, 115, 122, 121, 113], [106, 107, 116, 123, 122, 114], [107, 108, 117, 124, 123, 115], [108, 109, 118, 125, 124, 116], [109, 110, 119, 126, 125, 117], [110, 111, None, None, 126, 118], [112, 113, 121, None, None, None], [113, 114, 122, None, None, 120], [114, 115, 123, None, None, 121], [115, 116, 124, None, None, 122], [116, 117, 125, None, None, 123], [117, 118, 126, None, None, 124], [118, 119, None, None, None, 125]]

def get_next_node(node: int, rotation: int):
    return get_next_nodes()[node][rotation % 6]

def get_positions():
    return [(6, 0), (7, 0), (8, 0), (9, 0), (10, 0), (11, 0), (12, 0), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1), (10, 1), (11, 1), (12, 1), (4, 2), (5, 2), (6, 2), (7, 2), (8, 2), (9, 2), (10, 2), (11, 2), (12, 2), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (10, 3), (11, 3), (12, 3), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4), (10, 4), (11, 4), (12, 4), (1, 5), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5), (8, 5), (9, 5), (10, 5), (11, 5), (12, 5), (0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6), (10, 6), (11, 6), (12, 6), (0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (8, 7), (9, 7), (10, 7), (11, 7), (0, 8), (1, 8), (2, 8), (3, 8), (4, 8), (5, 8), (6, 8), (7, 8), (8, 8), (9, 8), (10, 8), (0, 9), (1, 9), (2, 9), (3, 9), (4, 9), (5, 9), (6, 9), (7, 9), (8, 9), (9, 9), (0, 10), (1, 10), (2, 10), (3, 10), (4, 10), (5, 10), (6, 10), (7, 10), (8, 10), (0, 11), (1, 11), (2, 11), (3, 11), (4, 11), (5, 11), (6, 11), (7, 11), (0, 12), (1, 12), (2, 12), (3, 12), (4, 12), (5, 12), (6, 12)]

def get_position(node: int):
    return get_positions()[node]

def Game(turn, reached_center, reached_side, player, opponent, graph, info):
    return namedtuple('Game', ['turn', 'reached_center', 'reached_side', 'player', 'opponent', 'graph', 'info'])(turn, reached_center, reached_side, player, opponent, graph, info)

def Player(node, rotation, playable_moves, playable_nodes):
    return namedtuple('Player', ['node', 'rotation', 'playable_moves', 'playable_nodes'])(node, rotation, playable_moves, playable_nodes)

def convert(board: ndarray, positions: list, rotations: list):
    def is_playable(position: tuple) -> bool:
        return 0 <= position[0] < 13 and 0 <= position[1] < 13 and 6 <= position[0] + position[1] < 19 and not board[position[1], position[0]].sum()

    def calculate_new_position(position: tuple, rotation: int, move: int = 0) -> ndarray:
        delta_x, delta_y = [(0, -1), (1, -1), (1, 0), (0, 1), (-1, 1), (-1, 0)][(rotation + move) % 6]
        return position[0] + delta_x, position[1] + delta_y

    turn = board.sum() // 2
    reached_center = board[6, 6].sum()
    reached_side = board[0, :].sum() or board[12, :].sum() or board[:, 0].sum() or board[:, 12].sum()

    player = Player(get_node(positions[0]), rotations[0], {}, {})
    opponent = Player(get_node(positions[1]), rotations[1], {}, {})

    for move in range(-2, 3):
        new_player_position = calculate_new_position(positions[0], rotations[0], move)
        if is_playable(new_player_position):
            player.playable_moves[move] = get_node(new_player_position)
            player.playable_nodes[get_node(new_player_position)] = move
        new_opponent_position = calculate_new_position(positions[1], rotations[1], move)
        if is_playable(new_opponent_position):
            opponent.playable_moves[move] = get_node(new_opponent_position)
            opponent.playable_nodes[get_node(new_opponent_position)] = move

    graph = zeros((127, 127), bool)

    for position in get_positions():
        node = get_node(position)
        for rotation in range(-3, 3):
            new_position = calculate_new_position(position, rotation)
            if is_playable(new_position):
                new_node = get_node(new_position)
                graph[node, new_node] = True
    player_position, player_rotation = array(positions[0]), rotations[0]
    opponent_position, opponent_rotation = array(positions[1]), rotations[1]
    return Game(turn, reached_center, reached_side, player, opponent, graph, (board, player_position, player_rotation, opponent_position, opponent_rotation))

def calculate_distance(game, node_a: int, node_b: int) -> int:
    if node_a == node_b:
        return 0
    
    distance = 127 * [None]

    queue = deque([node_a])
    distance[node_a] = 0
    targets = where(game.graph[node_b])[0].tolist()
    while len(queue) > 0:
        u = queue.popleft()

        if u in targets:
            return distance[u] + 1

        for v in where(game.graph[u])[0]:
            if distance[v] is None:
                distance[v] = distance[u] + 1
                queue.append(v)
    return distance[node_b]

def find_closest_node(game, node: int, targets: list) -> int:
    visited = 127 * [False]

    queue = deque([node])
    visited[node] = True
    while len(queue) > 0:
        node = queue.popleft()

        if node in targets:
            return node

        for new_node in where(game.graph[node])[0]:
            if not visited[new_node]:
                visited[new_node] = True
                queue.append(new_node)
    return None

def calculate_area(game, node: int, visited: list = None) -> int:
    count = 1
    visited = 127 * [False] if visited is None else visited.copy()

    queue = deque([node])
    visited[node] = True
    while len(queue) > 0:
        node = queue.popleft()

        for new_node in where(game.graph[node])[0]:
            if not visited[new_node]:
                count += 1
                visited[new_node] = True
                queue.append(new_node)
    return count

# optionally excluding u and v
def find_articulation_points(game, u=None, v=None):
    vis = 127 * [False]
    if u is not None: vis[u] = True
    if v is not None: vis[v] = True
    art = set()
    for u in range(127):
        if not vis[u]:
            if find_articulation_points_helper(game, u, None, vis, 127 * [1e9], 127 * [1e9], 0, art):
                art.add(u)
    return list(art)

def find_articulation_points_helper(game, u, parent, vis, num, low, cnt, art) -> int:
    rootChildren = 0
    num[u] = low[u] = cnt
    vis[u] = True
    cnt += 1
    for v in where(game.graph[u])[0]:
        if not game.graph[v][u]:
            continue
        if not vis[v]:
            find_articulation_points_helper(game, v, u, vis, num, low, cnt, art)
            if parent == None: rootChildren += 1
            if low[v] >= num[u] and parent != None: art.add(u)
            if low[v] > num[u]: pass # bridge
            low[u] = min(low[u], low[v])
        else:
            low[u] = min(low[u], num[v])
    return rootChildren > 1

def get_best_move_with_ray_casting(game) -> int:
    ratings = []
    for node, move in game.player.playable_nodes.items():
        maximal_area = 0
        
        visited = 127 * [False]

        ray_node = node
        ray_length = 1
        visited[ray_node] = True
        while True:
            new_node = get_next_node(ray_node, game.player.rotation + move)

            if new_node is None or not game.graph[ray_node, new_node] or visited[new_node]:
                break
            
            ray_node = new_node
            ray_length += 1
            visited[ray_node] = True

        for new_node in where(game.graph[ray_node])[0]:
            if not visited[new_node]:
                maximal_area = max(maximal_area, calculate_area(game, new_node, visited))

        ratings.append((maximal_area, move))

    mx = max(ratings)[0]
    return choice([move for rating, move in ratings if abs(mx - rating) < 1e-9])

def get_best_move_with_multi_ray_casting(game) -> int:
    ratings = []
    for player_node, player_move in game.player.playable_nodes.items():
        player_maximal_area = 0
        opponent_maximal_area = 0

        for opponent_node, opponent_move in game.opponent.playable_nodes.items():
            visited = 127 * [False]
            
            player_ray_node = player_node
            player_ray_length = 1
            visited[player_ray_node] = True

            opponent_ray_node = opponent_node
            opponent_ray_length = 1
            visited[opponent_ray_node] = True

            while player_ray_node != opponent_ray_node:
                new_player_node = get_next_node(player_ray_node, game.player.rotation + player_move)
                new_opponent_node = get_next_node(opponent_ray_node, game.opponent.rotation + opponent_move)

                is_new_player_node_not_playable = (new_player_node is None) or (not game.graph[player_ray_node, new_player_node]) or (visited[new_player_node])
                is_new_opponent_node_not_playable = (new_opponent_node is None) or (not game.graph[opponent_ray_node, new_opponent_node]) or (visited[new_opponent_node])
                
                if is_new_player_node_not_playable and is_new_opponent_node_not_playable: 
                    break
                
                if not is_new_player_node_not_playable:        
                    player_ray_node = new_player_node
                    player_ray_length += 1
                    visited[player_ray_node] = True
                if not is_new_opponent_node_not_playable:
                    opponent_ray_node = new_opponent_node
                    opponent_ray_length += 1
                    visited[opponent_ray_node] = True
        
            player_partial_maximum_area = 0
            for new_player_node in where(game.graph[player_ray_node])[0]:
                #if not visited[new_player_node]:
                    player_partial_maximum_area = max(player_partial_maximum_area, calculate_area(game, new_player_node, visited))
            opponent_partial_maximum_area = 0
            for new_opponent_node in where(game.graph[opponent_ray_node])[0]:
                #if not visited[new_opponent_node]:
                    opponent_partial_maximum_area = max(opponent_partial_maximum_area, calculate_area(game, new_opponent_node, visited))
            
            player_area = player_ray_length + player_partial_maximum_area
            opponent_area = opponent_ray_length + opponent_partial_maximum_area

            if opponent_area > opponent_maximal_area:
                opponent_maximal_area = opponent_area
                player_maximal_area = player_area
            elif opponent_area == opponent_maximal_area:
                player_maximal_area = max(player_maximal_area, player_area)

        ratings += [(player_maximal_area / (opponent_maximal_area if opponent_maximal_area != 0 else 1e-9), player_node, player_move)]
    mx = max(ratings)[0]
    distances = [(calculate_distance(game, game.opponent.node, node), move) for rating, node, move in ratings if abs(mx - rating) < 1e-9]
    if any([distance is None for distance, move in distances]):
        return choice([move for distance, move in distances if distance is None])
    return min([(distance, move) for distance, move in distances if distance is not None])[1]

def get_best_move_to_reach_node(game, node: int) -> int:
    distances = [(calculate_distance(game, node, other_node), other_node, move) for other_node, move in game.player.playable_nodes.items()]
    if any([distance is not None for distance, node, move in distances]):
        res = [(distance, node, move) for distance, node, move in distances if distance is not None]
        mn = min(res)[0]
        #game = game._replace(player=game.player._replace(playable_nodes={node: move for rating, node, move in res if abs(rating - mn) < 1e-9}))
    return get_best_move_by_filling(game)

def get_best_move_by_filling(game) -> int:
    ratings = []
    for player_node, player_move in game.player.playable_nodes.items():
        player_maximal_area = 0
        opponent_maximal_area = 0

        for opponent_node, opponent_move in game.opponent.playable_nodes.items():
            player_area = 0
            opponent_area = 0

            visited_on_turn = [[0, 0] for _ in range(127)]
            visited_on_turn[player_node][0] = 1
            visited_on_turn[opponent_node][1] = 1

            turn = 2
            queue = deque([(0, player_node, turn), (1, opponent_node, turn)])
            while len(queue) > 0:
                player, u, turn = queue.popleft()

                for v in where(game.graph[u])[0]:
                    if visited_on_turn[v] == [0, 0]:
                        if player == 0:
                            player_area += 1
                        else:
                            opponent_area += 1
                        visited_on_turn[v][player] = turn
                        queue.append((player, v, turn + 1))
                    elif visited_on_turn[v][1 - player] == turn:
                        if player == 0:
                            player_area += 0.5
                            opponent_area -= 0.5
                        else:
                            player_area -= 0.5
                            opponent_area += 0.5

            if opponent_area > opponent_maximal_area:
                opponent_maximal_area = opponent_area
                player_maximal_area = player_area
            elif opponent_area == opponent_maximal_area:
                player_maximal_area = max(player_maximal_area, player_area)

        ratings += [(player_maximal_area / (opponent_maximal_area if opponent_maximal_area != 0 else 1e-9), player_move)]
    
    mx = max(ratings)[0]
    moves = [move for rating, move in ratings if abs(mx - rating) < 1e-9]
    if len(moves) > 1:
        game = game._replace(player=game.player._replace(playable_moves={move: game.player.playable_moves[move] for move in moves}, playable_nodes={game.player.playable_moves[move]: move for move in moves}))
        return get_best_move_with_ray_casting(game)
    return moves[0]

def get_best_move(game) -> int:
    if len(game.player.playable_nodes) == 0:
        return 0
    elif len(game.opponent.playable_nodes) == 0:
        return list(game.player.playable_nodes.values())[0]

    player_playable_areas = [(calculate_area(game, node), node, move) for node, move in game.player.playable_nodes.items()]
    player_unique_areas = len(set([area for area, node, move in player_playable_areas]))

    if player_unique_areas >= 2:
        mx = max(player_playable_areas)[0]
        moves = [move for area, node, move in player_playable_areas if abs(mx - area) < 1e-9]
        game = game._replace(player=game.player._replace(playable_moves={move: game.player.playable_moves[move] for move in moves}, playable_nodes={game.player.playable_moves[move]: move for move in moves}))
    
    if all(calculate_distance(game, game.player.node, node) is None for node in game.opponent.playable_nodes):
        articulation_points = find_articulation_points(game)
        moves = [move for node, move in game.player.playable_nodes.items() if node not in articulation_points]
        if len(moves) == 0:
            moves = [move for node, move in game.player.playable_nodes.items()]
        else:
            ratings = []
            for u, move in game.player.playable_nodes.items():
                if u not in articulation_points:
                    mx = len(find_articulation_points(game, u))
                    for v in where(game.graph[u])[0]:
                        if not game.graph[v][u]:
                            continue
                        mx = max(mx, len(find_articulation_points(game, u, v)))
                    ratings += [(mx, move)]
            mn = min(ratings)[0]
            moves = [move for rating, move in ratings if abs(rating - mn) < 1e-9]
        game = game._replace(player=game.player._replace(playable_moves={move: game.player.playable_moves[move] for move in moves}, playable_nodes={game.player.playable_moves[move]: move for move in moves}))
        return get_best_move_with_ray_casting(game)

    if game.turn < 7 and not game.reached_center and game.reached_side and game.opponent.node in [63, 76, 75, 62, 50, 51, 64] and 63 in game.player.playable_nodes:
        new_game = game._replace(graph=game.graph.copy())
        new_game.graph[63, :] = False
        new_game.graph[:, 63] = False

        move_to_center = new_game.player.playable_nodes[63]
        move_to_left = move_to_center - 1
        move_to_right = move_to_center + 1
        
        area_left = calculate_area(new_game, game.player.playable_moves[move_to_left])
        area_right = calculate_area(new_game, game.player.playable_moves[move_to_right])
        if area_left - area_right >= 1:
            return move_to_left
        elif area_left - area_right <= -1:
            return move_to_right
    return get_best_move_by_filling(game)

def generate_move(board: ndarray, positions: list, rotations: list) -> int:
    t0 = time()

    game = convert(board, positions, rotations)
    move = get_best_move(game)
    
    t = time() - t0
    assert t <= 1, "Exceeded execution time with %.3f seconds" % t

    return move
