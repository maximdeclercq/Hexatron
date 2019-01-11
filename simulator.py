import importlib
import json
import os
import sys
import time

sys.path.append('simulator-files')
from game import Hexatron

sys.path.append('agents')
sys.path.append('agents/old')

def run_simulation(agent_one_file, agent_two_file):
    """Set up a single game, where two agents play each other.
    A replay will be written to "replay.html".

    Args:
        agent_one_file (string): Filename for the first agent.
        agent_two_file (string): Filename for the second agent.
    """

    print('Running a simulation with "{}" vs. "{}".'.format(
        agent_one_file, agent_two_file))

    agent_one_module, _ = os.path.splitext(agent_one_file)
    generator_one_module = importlib.import_module(agent_one_module)

    agent_two_module, _ = os.path.splitext(agent_two_file)
    generator_two_module = importlib.import_module(agent_two_module)

    # Instantiate game
    game = Hexatron(13)
    observation = game.reset()

    # Play game
    done = False
    while not done:

        # Generate moves
        move1 = generator_one_module.generate_move(
            observation['board'],
            observation['positions'],
            observation['orientations'])

        move2 = generator_two_module.generate_move(
            observation['board'][:, :, ::-1],
            observation['positions'][::-1],
            observation['orientations'][::-1])

        observation, done, status = game.act(move1, move2)

    # Generate replay
    with open('simulator-files/html.template', 'r', encoding='utf8') as infile:
        template = infile.read()

    output = template.replace('{{AGENT_1}}', agent_one_module)
    output = output.replace('{{AGENT_2}}', agent_two_module)

    output = output.replace(
        '{{GENERATED_TRAJECTORY}}',
        json.dumps([p.trajectory for p in game.players]))

    tid = int(time.time() * 1e6)
    with open('replays/replay%d.html' % tid, 'w', encoding='utf8') as outfile:
        outfile.write(output)

    print('A replay of the simulation has been written to "replays/replay%d.html".' % tid)


def main(argv):
    """Script starting point.

    Args:
        argv (list): List of command-line arguments. The first element is
            always "simulator.py", the name of this script. The second element
            should be the name of the first agent's file. The final element
            should be the name of the opponent's file. Not that this can be
            the same name as the previous file.
    """

    if len(argv) != 3:
        print('Usage: python[3] simulator.py [agent_one] [agent_two]')
        exit(1)

    run_simulation(*argv[1:])


if __name__ == '__main__':
    main(sys.argv)
