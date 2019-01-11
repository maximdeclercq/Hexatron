import numpy as np


def generate_move(board, positions, orientations):
    """Generate a move.

    Args:
        board (np.array): The playing field, represented as 3D array.
        positions (list): A list of my position, as tuple `(x, y)`, and my
            opponents position.
        orientations (list): A list of my orientation (integer in [0,5]),
            and my opponent's orientation.

    Returns:
        move (int): An integer in [-2,2].
    """

    move = get_stochastic_move()
    return move


def get_stochastic_move():
    """Go forward most of the time, but with a small probability,
    take a turn.
    """

    rand = np.random.rand()

    # Go left
    if rand < 0.1:
        return -1

    # Go right
    if rand > 0.9:
        return 1

    # Go straight
    return 0
