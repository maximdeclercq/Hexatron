from numpy import ndarray, array, array_equal, where, zeros
from time import time
from random import choice
from collections import deque, namedtuple

# Geef weer of een rij in een lijst te vinden is
def is_array_in_list(a: ndarray, l: list):
    return any(array_equal(a, e) for e in l)

# Geeft een rotatie weer als een richting op het bord in x en y coordinaten
def rotation_to_position(rotation: int) -> ndarray:
    return array([(0, -1), (1, -1), (1, 0), (0, 1), (-1, 1), (-1, 0)][rotation % 6])

# Berekent de nieuwe positie en rotatie indien een move uitgevoerd 
def calculate_new_state(position: ndarray, rotation: int, move: int = 0) -> ndarray:
    return position + rotation_to_position(rotation + move), (rotation + move) % 6

# Geeft weer of een positie geldig is op het bord
def is_allowed(position: ndarray) -> bool:
    return 0 <= position[0] < 13 and 0 <= position[1] < 13 and 6 <= position[0] + position[1] < 19

# Geeft weer of een positie speelbaar is op het bord
def is_playable(board: ndarray, position: ndarray) -> bool:
    return is_allowed(position) and not board[position[1], position[0], 0] and not board[position[1], position[0], 1]

# Berekent de afstand tussen twee posities op het bord
def calculate_distance_between(board: ndarray, position_a: ndarray, position_b: ndarray) -> int:
    new_board = board.copy()
    new_board[position_a[1], position_a[0], 0] = 1
    new_board[position_b[1], position_b[0], 1] = 0

    queue = deque([(position_a, 1)])
    while len(queue) > 0:
        position, distance = queue.popleft()

        if array_equal(position, position_b):
            return distance

        for i in range(-3, 3):
            new_position, _ = calculate_new_state(position, 0, i)

            if is_playable(new_board, new_position):
                queue.append((new_position, distance + 1))
                new_board[new_position[1], new_position[0], 0] = 1
    return None

# Zoekt naar een positie in de targets lijst die het dichts bij een andere positie ligt
def find_closest_position(board: ndarray, position: ndarray, targets: list):
    new_board = board.copy()

    queue = deque([position])
    while len(queue) > 0:
        position = queue.popleft()

        for i in range(-3, 3):
            new_position, _ = calculate_new_state(position, 0, i)

            if is_array_in_list(position, targets):
                return position
            if is_playable(new_board, new_position):
                new_board[new_position[1], new_position[0], 0] = 1
                queue.append(new_position)
    return None

# Berekent de omsloten oppervlakte die beschikbaar is vanuit een positie
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
                new_board[new_position[1], new_position[0], 0] = 1
                count += 1
    return count

# Geeft de move die in de richting van target gaat (enkel relevant indien target bereikbaar is)
def get_best_move_with_targeting(board: ndarray, position: ndarray, rotation: int, playable_moves: list, target: ndarray) -> int:
    playable_positions_with_moves = [(calculate_new_state(position, rotation, move)[0], move) for move in playable_moves]
    playable_positions = [position for position, move in playable_positions_with_moves]
    playable_positions_equal = [position for position in playable_positions if position[0] == 12 - position[1]]
    if len(playable_positions_equal) > 0:
        closest_position = find_closest_position(board, target, playable_positions_equal)
    else:
        closest_position = find_closest_position(board, target, playable_positions)
    res = [move for position, move in playable_positions_with_moves if array_equal(position, closest_position)]
    return choice(res) if closest_position is not None and len(res) > 0 else choice(playable_moves)

# Geef de move die de grootste oppervlakte kiest (enkel relevant indien men op dat moment tussen 2 gebieden kan kiezen)
def get_best_move_with_floodfill(board: ndarray, position: ndarray, rotation: int, playable_moves: list) -> int:
    playable_areas = [(calculate_available_area(board, calculate_new_state(position, rotation, move)[0]), move) for move in playable_moves]
    return max(playable_areas)[1]

# Geef de move die resulteert in de grootste oppervlakte indien we in die richting zouden blijven gaan tot we botsen
# Deze functie werd gedegradeerd tot een tiebreaker voor andere algoritmes
def get_best_move_with_ray_casting(board: ndarray, player_position: ndarray, player_rotation: int, player_playable_moves: list) -> int:
    ratings = []
    for player_move in player_playable_moves:
        new_player_position, new_player_rotation = calculate_new_state(player_position, player_rotation, player_move)

        player_maximal_area = 0
        
        new_board = board.copy()
        new_board[new_player_position[1], new_player_position[0], 0] = 1

        player_ray_position = new_player_position.copy()
        player_ray_length = 1
        while True:
            new_player_ray_position, new_player_rotation = calculate_new_state(player_ray_position, new_player_rotation)

            is_new_player_ray_position_playable = is_playable(new_board, new_player_ray_position)

            if not is_new_player_ray_position_playable:
                break
            
            player_ray_position = new_player_ray_position
            player_ray_length += 1
            new_board[player_ray_position[1], player_ray_position[0], 0] = 1

        for move in range(-2, 3):
            new_player_ray_position, _ = calculate_new_state(player_ray_position, new_player_rotation, move)

            is_new_player_ray_position_playable = is_playable(new_board, new_player_ray_position)
            
            if is_new_player_ray_position_playable:
                player_maximal_area = max(player_maximal_area, calculate_available_area(new_board, new_player_ray_position))

        ratings += [(player_maximal_area, player_move)]

    mx = max(ratings)[0]
    return choice([move for rating, move in ratings if abs(mx - rating) < 1e-9])

# Geeft de move die resulteert in de grootste verhouding tussen de maximale oppervlaktes van de speler en tegenstander indien we in die richting zouden blijven gaan tot we botsen,
# terwijl we tegelijkertijd voor hetzelfde doen voor alle mogelijke moves van de tegenstander.
# Deze functie werd gedegradeerd tot een tiebreaker voor andere algoritmes
def get_best_move_with_multi_ray_casting(board: ndarray, player_position: ndarray, player_rotation: int, opponent_position: ndarray, opponent_rotation: int, player_playable_moves:list, opponent_playable_moves:list) -> int:
    ratings = []
    for player_move in player_playable_moves:
        new_player_position, new_player_rotation = calculate_new_state(player_position, player_rotation, player_move)

        player_maximal_area = 0
        opponent_maximal_area = 0

        for opponent_move in opponent_playable_moves:
            new_opponent_position, new_opponent_rotation = calculate_new_state(opponent_position, opponent_rotation, opponent_move)

            new_board = board.copy()
            new_board[new_player_position[1], new_player_position[0], 0] = 1
            new_board[new_opponent_position[1], new_opponent_position[0], 1] = 1

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
                    new_board[player_ray_position[1], player_ray_position[0], 0] = 1

                if is_new_opponent_ray_position_playable:
                    opponent_ray_position = new_opponent_ray_position
                    opponent_ray_length += 1
                    new_board[opponent_ray_position[1], opponent_ray_position[0], 1] = 1
            
            player_partial_maximum_area = 0
            opponent_partial_maximum_area = 0
            for move in range(-2, 3):
                new_player_ray_position, _ = calculate_new_state(player_ray_position, new_player_rotation, move)
                new_opponent_ray_position, _ = calculate_new_state(opponent_ray_position, new_opponent_rotation, move)

                is_new_player_ray_position_playable = is_playable(new_board, new_player_ray_position)
                is_new_opponent_ray_position_playable = is_playable(new_board, new_opponent_ray_position)

                if is_new_player_ray_position_playable:
                    player_partial_maximum_area = max(player_partial_maximum_area, calculate_available_area(new_board, new_player_ray_position))

                if is_new_opponent_ray_position_playable:
                    opponent_partial_maximum_area = max(opponent_partial_maximum_area, calculate_available_area(new_board, new_opponent_ray_position))
            
            player_area = player_ray_length + player_partial_maximum_area
            opponent_area = opponent_ray_length + opponent_partial_maximum_area

            if opponent_area > opponent_maximal_area:
                opponent_maximal_area = opponent_area
                player_maximal_area = player_area
            elif opponent_area == opponent_maximal_area:
                player_maximal_area = max(player_maximal_area, player_area)

        ratings += [(player_maximal_area / (opponent_maximal_area if opponent_maximal_area != 0 else 1e-9), player_move)]

    # Als we hier nog geen definitieve beslissing gemaakt hebben, kiezen we voor de move die het meest naar de andere speler gaat
    mx = max(ratings)[0]
    distances = [(calculate_distance_between(board, calculate_new_state(player_position, player_rotation, move)[0], opponent_position), move) for rating, move in ratings if abs(mx - rating) < 1e-9]
    if any([distance is None for distance, move in distances]):
        return choice([move for distance, move in distances if distance is None])
    return min([(distance, move) for distance, move in distances if distance is not None])[1]

# Geeft de move die ervoor zorgt dat we een maximaal aantal vakjes als eerste kunnen bereiken
# indien we een vakje tegelijk kunnen bereiken telt dit als een half vakje 
def get_best_move_with_flooding(board: ndarray, player_position: ndarray, player_rotation: int, opponent_position: ndarray, opponent_rotation: int, player_playable_moves:list, opponent_playable_moves:list) -> int:
    ratings = []
    for player_move in player_playable_moves:
        new_player_position, new_player_rotation = calculate_new_state(player_position, player_rotation, player_move)

        player_maximal_area = 0
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
        return get_best_move_with_multi_ray_casting(board, player_position, player_rotation, opponent_position, opponent_rotation, moves, opponent_playable_moves)
    return moves[0]

# GRAPH
def get_nodes():
    return {(6, 0): 0, (7, 0): 1, (8, 0): 2, (9, 0): 3, (10, 0): 4, (11, 0): 5, (12, 0): 6, (5, 1): 7, (6, 1): 8, (7, 1): 9, (8, 1): 10, (9, 1): 11, (10, 1): 12, (11, 1): 13, (12, 1): 14, (4, 2): 15, (5, 2): 16, (6, 2): 17, (7, 2): 18, (8, 2): 19, (9, 2): 20, (10, 2): 21, (11, 2): 22, (12, 2): 23, (3, 3): 24, (4, 3): 25, (5, 3): 26, (6, 3): 27, (7, 3): 28, (8, 3): 29, (9, 3): 30, (10, 3): 31, (11, 3): 32, (12, 3): 33, (2, 4): 34, (3, 4): 35, (4, 4): 36, (5, 4): 37, (6, 4): 38, (7, 4): 39, (8, 4): 40, (9, 4): 41, (10, 4): 42, (11, 4): 43, (12, 4): 44, (1, 5): 45, (2, 5): 46, (3, 5): 47, (4, 5): 48, (5, 5): 49, (6, 5): 50, (7, 5): 51, (8, 5): 52, (9, 5): 53, (10, 5): 54, (11, 5): 55, (12, 5): 56, (0, 6): 57, (1, 6): 58, (2, 6): 59, (3, 6): 60, (4, 6): 61, (5, 6): 62, (6, 6): 63, (7, 6): 64, (8, 6): 65, (9, 6): 66, (10, 6): 67, (11, 6): 68, (12, 6): 69, (0, 7): 70, (1, 7): 71, (2, 7): 72, (3, 7): 73, (4, 7): 74, (5, 7): 75, (6, 7): 76, (7, 7): 77, (8, 7): 78, (9, 7): 79, (10, 7): 80, (11, 7): 81, (0, 8): 82, (1, 8): 83, (2, 8): 84, (3, 8): 85, (4, 8): 86, (5, 8): 87, (6, 8): 88, (7, 8): 89, (8, 8): 90, (9, 8): 91, (10, 8): 92, (0, 9): 93, (1, 9): 94, (2, 9): 95, (3, 9): 96, (4, 9): 97, (5, 9): 98, (6, 9): 99, (7, 9): 100, (8, 9): 101, (9, 9): 102, (0, 10): 103, (1, 10): 104, (2, 10): 105, (3, 10): 106, (4, 10): 107, (5, 10): 108, (6, 10): 109, (7, 10): 110, (8, 10): 111, (0, 11): 112, (1, 11): 113, (2, 11): 114, (3, 11): 115, (4, 11): 116, (5, 11): 117, (6, 11): 118, (7, 11): 119, (0, 12): 120, (1, 12): 121, (2, 12): 122, (3, 12): 123, (4, 12): 124, (5, 12): 125, (6, 12): 126}

def get_node(position: tuple):
    return get_nodes()[position]

def get_positions():
    return [(6, 0), (7, 0), (8, 0), (9, 0), (10, 0), (11, 0), (12, 0), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1), (10, 1), (11, 1), (12, 1), (4, 2), (5, 2), (6, 2), (7, 2), (8, 2), (9, 2), (10, 2), (11, 2), (12, 2), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (10, 3), (11, 3), (12, 3), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4), (10, 4), (11, 4), (12, 4), (1, 5), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5), (8, 5), (9, 5), (10, 5), (11, 5), (12, 5), (0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6), (10, 6), (11, 6), (12, 6), (0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (8, 7), (9, 7), (10, 7), (11, 7), (0, 8), (1, 8), (2, 8), (3, 8), (4, 8), (5, 8), (6, 8), (7, 8), (8, 8), (9, 8), (10, 8), (0, 9), (1, 9), (2, 9), (3, 9), (4, 9), (5, 9), (6, 9), (7, 9), (8, 9), (9, 9), (0, 10), (1, 10), (2, 10), (3, 10), (4, 10), (5, 10), (6, 10), (7, 10), (8, 10), (0, 11), (1, 11), (2, 11), (3, 11), (4, 11), (5, 11), (6, 11), (7, 11), (0, 12), (1, 12), (2, 12), (3, 12), (4, 12), (5, 12), (6, 12)]

def get_position(node: tuple):
    return get_positions()[node]

def Game(player, opponent, graph):
    return namedtuple('Game', ['player', 'opponent', 'graph'])(player, opponent, graph)

def Player(node, playable_nodes):
    return namedtuple('Player', ['node', 'playable_nodes'])(node, playable_nodes)

def convert(board: ndarray, positions: list, rotations: list):
    def is_playable(position: tuple) -> bool:
        return 0 <= position[0] < 13 and 0 <= position[1] < 13 and 6 <= position[0] + position[1] < 19 and not board[position[1], position[0]].sum()

    def calculate_new_position(position: tuple, rotation: int, move: int = 0) -> ndarray:
        delta_x, delta_y = [(0, -1), (1, -1), (1, 0), (0, 1), (-1, 1), (-1, 0)][(rotation + move) % 6]
        return position[0] + delta_x, position[1] + delta_y

    player = Player(get_node(positions[0]), {})
    opponent = Player(get_node(positions[1]), {})

    for move in range(-2, 3):
        new_player_position = calculate_new_position(positions[0], rotations[0], move)
        if is_playable(new_player_position):
            player.playable_nodes[get_node(new_player_position)] = move
        new_opponent_position = calculate_new_position(positions[1], rotations[1], move)
        if is_playable(new_opponent_position):
            opponent.playable_nodes[get_node(new_opponent_position)] = move

    graph = zeros((127, 127), bool)

    for position in get_positions():
        node = get_node(position)
        for rotation in range(-3, 3):
            new_position = calculate_new_position(position, rotation)
            if is_playable(new_position):
                new_node = get_node(new_position)
                graph[node, new_node] = True

    return Game(player, opponent, graph)

# excluding node (default None)
def find_articulation_points(game, node=None):
    vis = 127 * [False]
    if node is not None: vis[node] = True
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
            low[u] = min(low[u], low[v])
        else:
            low[u] = min(low[u], num[v])
    return rootChildren > 1

def get_best_move_to_fill(game) -> int:
    articulation_points = find_articulation_points(game)
    moves = [move for node, move in game.player.playable_nodes.items() if node not in articulation_points]
    if moves == []:
        moves = list(game.player.playable_nodes.values())
    return choice(moves)

# /GRAPH

def get_best_move(board: ndarray, player_position: ndarray, player_rotation: int, opponent_position: ndarray, opponent_rotation: int, game):
    player_playable_moves = [move for move in range(-2, 3) if is_playable(board, calculate_new_state(player_position, player_rotation, move)[0])]
    if player_playable_moves == []: return 0
    
    opponent_playable_moves = [move for move in range(-2, 3) if is_playable(board, calculate_new_state(opponent_position, opponent_rotation, move)[0])]
    if opponent_playable_moves == []: return player_playable_moves[0]

    player_playable_areas = [(calculate_available_area(board, calculate_new_state(player_position, player_rotation, move)[0]), move) for move in player_playable_moves]
    player_unique_areas = len(set([area for area, move in player_playable_areas]))

    if player_unique_areas >= 2:
        mx = max(player_playable_areas)[0]
        player_playable_moves = [move for area, move in player_playable_areas if abs(mx - area) < 1e-9]
        
    if calculate_distance_between(board, player_position, opponent_position) is None:
        return get_best_move_to_fill(game)

    if board.sum() // 2 < 7 and board[6, 6].sum() == 0 and (board[0, :].sum() or board[12, :].sum() or board[:, 0].sum() or board[:, 12].sum()):
        opponent_is_close_to_middle = False
        for opponent_move in range(-2, 3):
            new_opponent_position, _ = calculate_new_state(opponent_position, opponent_rotation, opponent_move)
            if array_equal(new_opponent_position, array([6, 6])):
                opponent_is_close_to_middle = True
        
        if not opponent_is_close_to_middle:
            return get_best_move_with_targeting(board, player_position, player_rotation, player_playable_moves, array([6, 6]))
        else:
            new_board = board.copy()
            new_board[6, 6, 1] = 1
            new_player_position_left, _ = calculate_new_state(player_position, player_rotation, -1)
            new_player_position_right, _ = calculate_new_state(player_position, player_rotation, 1)
            area_left = calculate_available_area(new_board, new_player_position_left)
            area_right = calculate_available_area(new_board, new_player_position_right)
            if area_left - area_right >= 1:
                return -1
            elif area_left - area_right <= -1:
                return 1
    
    return get_best_move_with_flooding(board, player_position, player_rotation, opponent_position, opponent_rotation, player_playable_moves, opponent_playable_moves)

def generate_move(board: ndarray, positions: list, rotations: list) -> int:
    player_position, player_rotation = array(positions[0]), rotations[0]
    opponent_position, opponent_rotation = array(positions[1]), rotations[1]

    game = convert(board, positions, rotations)

    t0 = time()

    move = get_best_move(board, player_position, player_rotation, opponent_position, opponent_rotation, game)

    t = time() - t0
    assert t <= 1, "Exceeded execution time with %.3f seconds" % t

    return move
