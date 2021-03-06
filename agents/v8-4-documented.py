from numpy import ndarray, array, array_equal
from time import time
from random import choice
from collections import deque

# Geeft weer of een rij in een lijst te vinden is
def is_array_in_list(a: ndarray, l: list):
    return any(array_equal(a, e) for e in l)

# Geeft een rotatie weer als een richting op het bord in x en y coordinaten
def rotation_to_position(rotation: int) -> ndarray:
    return array([(0, -1), (1, -1), (1, 0), (0, 1), (-1, 1), (-1, 0)][rotation % 6])

# Berekent de nieuwe positie en rotatie indien een move uitgevoerd wordt
def calculate_new_state(position: ndarray, rotation: int, move: int = 0) -> ndarray:
    return position + rotation_to_position(rotation + move), (rotation + move) % 6

# Geeft weer of een positie geldig is op het bord
def is_allowed(board: ndarray, position: ndarray) -> bool:
    return 0 <= position[0] < 13 and 0 <= position[1] < 13 and 6 <= position[0] + position[1] < 19

# Geeft weer of een positie speelbaar is op het bord
def is_playable(board: ndarray, position: ndarray) -> bool:
    return is_allowed(board, position) and not board[position[1], position[0], 0] and not board[position[1], position[0], 1]

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

# Berekent het aantal vakjes dat bereikbaar is vanuit een positie
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

# Geef de move die resulteert in de grootste oppervlakte indien we in die richting zouden blijven gaan tot we botsen
# Deze functie wordt hier gebruikt om gebieden op te vullen
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

    mx = max(ratings)[0]
    # Als we hier nog geen definitieve beslissing gemaakt hebben, kiezen we voor de move die het meest naar de andere speler gaat
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

# Geeft de best mogelijke move
def get_best_move(board: ndarray, player_position: ndarray, player_rotation: int, opponent_position: ndarray, opponent_rotation: int):
    player_playable_moves = [move for move in range(-2, 3) if is_playable(board, calculate_new_state(player_position, player_rotation, move)[0])]
    if player_playable_moves == []: return 0
    
    opponent_playable_moves = [move for move in range(-2, 3) if is_playable(board, calculate_new_state(opponent_position, opponent_rotation, move)[0])]
    if opponent_playable_moves == []: return player_playable_moves[0]

    player_playable_areas = [(calculate_available_area(board, calculate_new_state(player_position, player_rotation, move)[0]), move) for move in player_playable_moves]
    player_unique_areas = len(set([area for area, move in player_playable_areas]))

    # Als er meer dan 1 gebied beschikbaar is, beperken we ons tot de grootste gebieden
    if player_unique_areas >= 2:
        mx = max(player_playable_areas)[0]
        player_playable_moves = [move for area, move in player_playable_areas if abs(mx - area) < 1e-9]
    
    # Als we de andere speler niet kunnen bereiken, vullen we het gebied op
    if calculate_distance_between(board, player_position, opponent_position) is None:
        return get_best_move_with_ray_casting(board, player_position, player_rotation, player_playable_moves)

    # Als we in het begin van het spel zijn, het midden is nog niet bereikt en de randen zijn wel al bereikt (bv. omdat de spelers daar gestart zijn)
    if board.sum() // 2 < 7 and board[6, 6].sum() == 0 and (board[0, :].sum() or board[12, :].sum() or board[:, 0].sum() or board[:, 12].sum()):
        opponent_is_close_to_middle = False
        for opponent_move in range(-2, 3):
            new_opponent_position, _ = calculate_new_state(opponent_position, opponent_rotation, opponent_move)
            if array_equal(new_opponent_position, array([6, 6])):
                opponent_is_close_to_middle = True
        
        # Als de tegenstander het midden niet direct kan innemen, gaan we er naartoe
        if not opponent_is_close_to_middle:
            return get_best_move_with_targeting(board, player_position, player_rotation, player_playable_moves, array([6, 6]))
        # Anders kijken we of we de tegenstander eventueel kunnen afsnijden als er links of rechts een groot gebied is
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
    
    # In alle andere gevallen steunen we op het algemene algoritme
    return get_best_move_with_flooding(board, player_position, player_rotation, opponent_position, opponent_rotation, player_playable_moves, opponent_playable_moves)

def generate_move(board: ndarray, positions: list, rotations: list) -> int:
    player_position, player_rotation = array(positions[0]), rotations[0]
    opponent_position, opponent_rotation = array(positions[1]), rotations[1]

    t0 = time()

    move = get_best_move(board, player_position, player_rotation, opponent_position, opponent_rotation)

    t = time() - t0
    assert t <= 1, "Exceeded execution time with %.3f seconds" % t

    return move
