import numpy as np


class Status:
    VALID = 0
    CRASHED_INTO_WALL = 1
    CRASHED_INTO_OPPONENT = 2


class Player:

    STEPS = [(-1, 0),  # NW
             (-1, 1),  # NE
             (0, 1),   # E
             (1, 0),   # SE
             (1, -1),  # SW
             (0, -1)]  # W

    def __init__(self, y, x, orientation):
        """Constructor.

        Args:
            y (int): The Y-coordinate of the player.
            x (int): The X-coordinate of the player.
            orientation (int): The orientation of the player.
        """

        self.y = y
        self.x = x
        self.orientation = int(orientation)

        self.trajectory = [{
            'x': self.x, 'y': self.y, 'orientation': self.orientation}]

    def act(self, action):
        """Rotate according to `action`, and move 1 step forward.

        Args:
            action (int): One of:
                -2: big turn left
                -1: small turn left
                 0: go straight
                 1: small turn right
                 2: big turn right
        """

        self.orientation = int((self.orientation + action) % 6)
        dy, dx = Player.STEPS[self.orientation]
        self.y += dy
        self.x += dx

        self.trajectory.append({
            'x': self.x, 'y': self.y, 'orientation': self.orientation})

    def frontal_crash(self, other):
        """Check if this player's head collides
        with the head of another player.

        Args:
            other (Player): The other player.

        Returns:
            frontal_crash (bool): True if both player's heads collide.
        """

        frontal_crash = self.y == other.y and self.x == other.x
        return frontal_crash


class Hexatron:

    def __init__(self, size=11):
        """Constructor.

        Args:
            size (int): Size of the (outer) square grid, that will contain the
                hexagonal playing field.
        """

        self.size = size
        self.halfsize = size // 2

    def reset(self):
        """Initialize the playing field, and semi-randomly iniatialize
        player 1 to the bottom left of the playing field, and player 2 to the
        bottom right of the playing field.

        Returns:
            observation (dict): See `_get_observation`.
        """

        self.grid = np.zeros([self.size, self.size, 2])

        # Initialize
        #   - player 1 bottom left
        #   - player 2 top right
        vertical_distance = np.random.randint(4)
        horizontal_distance = np.random.randint(4)

        self.players = [
            Player(
                self.size - 1 - vertical_distance,
                horizontal_distance,
                np.random.choice([1, 2])),
            Player(
                vertical_distance,
                self.size - 1 - horizontal_distance,
                np.random.choice([4, 5]))]

        self._update()
        observation = self._get_observation()
        return observation

    def _update(self):
        """Set the players' positions in the grid."""

        for idx, player in enumerate(self.players):
            self.grid[player.y, player.x, idx] = 1

    def _get_observation(self):
        """Return a view of the game.

        Returns:
            observation (dict): Observation dictionary, containing:
                - board (np.array): A 3d array representation the playing
                    field
                - positions (tuple): A tuple of length 2, containing the
                    coordinates for both players
                - orientations (tuple): A tuple of length 2, containing the
                    orientations for both players
        """

        observation = {
            'board': self.grid.copy(),
            'positions': tuple([(p.x, p.y) for p in self.players]),
            'orientations': tuple([p.orientation for p in self.players])}

        return observation

    def act(self, *actions):
        """Move both players.

        Args:
            actions (List[int]): A list containing the action for player 1
                and player 2. Actions are:
                    -2: big turn left
                    -1: small turn left
                     0: go straight
                     1: small turn right
                     2: big turn right

        Returns:
            observation (dict): See `_get_observation`.
            done (bool): True if the game is over, meaning either one or both
                players have crashed.
            status (List[int]): A list containing the status for player 1
                and player 2. Status are:
                    0: the player has a valid position
                    1: the player crashed into a wall
                    2: the player crashed into a tail
        """

        done = False
        status = [0, 0]

        # Valid position on the playing field
        for player, action in zip(self.players, actions):
            player.act(action)

        # Valid position on the field, not crashed into a tail
        for idx, (player, opponent) in enumerate(
                zip(self.players, reversed(self.players))):
            status[idx] = self._validate_player(player, opponent)

        if sum(status) > 0:
            done = True

        if not done:
            self._update()

        observation = self._get_observation()
        return observation, done, status

    def _validate_player(self, player, opponent):
        """Check if a player is in a legal state.

        Args:
            player (Player): The player.

        Returns:
            status (int): The status for the player:
                0: the player has a valid position
                1: the player crashed into a wall
                2: the player crashed into a tail
        """

        status = 0

        # Position
        status = self._validate_position(player)

        if status > 0:
            return status

        # Unoccupied space (by a TAIL)
        status = self._validate_crash(player)

        if status > 0:
            return status

        # Frontal crash
        status = player.frontal_crash(opponent)
        return status

    def _validate_position(self, player):
        """Check if a player resides inside the hexagonal playing field.

        Args:
            player (Player): The player.

        Returns:
            status (int): The status for the player:
                0: the player has a valid position
                1: the player crashed into a wall
        """

        if (player.x < 0 or player.x >= self.size or
                player.y < 0 or player.y >= self.size or
                player.x + player.y < self.halfsize or
                player.x + player.y >= self.size + self.halfsize):
            return Status.CRASHED_INTO_WALL

        return Status.VALID

    def _validate_crash(self, player):
        """Check if a player's position colides with a tail.

        Args:
            player (Player): The player.

        Returns:
            status (int): The status for the player:
                0: the player has a valid position
                2: the player crashed into a tail
        """

        if np.sum(self.grid, axis=2)[player.y, player.x] > 0:
            return Status.CRASHED_INTO_OPPONENT

        return Status.VALID

    def _validate_frontal_crash(self, player1, player2):
        """Check if two players' heads collide.

        Args:
            player1 (Player): Player 1.
            player2 (Player): Player 2.

        Returns:
            status (int): The status for the player:
                0: the player has a valid position
                2: the player crashed into his opponent's head
        """

        if player1.frontal_crash(player2):
            Status.CRASHED_INTO_OPPONENT

        return Status.VALID
