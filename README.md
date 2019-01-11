# Hexatron
Informatica challenge 2018 solution by Maxim De Clercq (#1 in play-offs)

## Write-up
The final agent has two major versions, v8 and v10, where v10 has almost the exact same strategy as v8 except it’s much faster because it represents the board as a graph (which I’ll explain later). 

Both agents have a large set of utility functions that allow to write code much faster because these can be copied between versions since their implementation stays the same (e.g. is position x playable? How many cells can the agent reach from position x? What is the distance between position x and y? What is the closest position in set s to position x?).

The rest of the code consists of algorithms to determine the best move. Most of these algorithms filter the moves that are playable and passes them on to another algorithm to break ties. The first algorithm determines if we must decide between two or more areas, and only passes the moves that lead to the larger area. Then the agent checks if we can reach the opponent, if that’s not possible, we can just fill the remaining area with a filler algorithm.

In all other cases it’s almost always optimal to go to the center of the board. If the agent is about to go to the center of the board, it first checks if the opponent can reach the center too. If he can, then the agent can possibly cut off the opponent by moving slightly to the left or slightly to the right, but only if the start positions were at the edge of the board and if cutting off results in a larger area than the area of the opponent. 

If none of the above special cases occurred, the agent falls back on its general flooding algorithm, which makes the move with results in the most cells that it can reach first. If the opponent can reach a cell at the same time as the agent, it counts as half a cell.

If the flooding results in equal scores for several moves, it passes those moves to the multi ray casting algorithm, which is a rather old algorithm (v6) that casts rays from the position of both players and determines which move results in the largest area.

The biggest difference between v8 and v10 lies in the filler algorithm. While v8 only casts single rays from the players position to determine the largest possible area, v10 composes a graph from the grid. This is done by mapping every position in the grid to a number from 0 till 126. Because ray casting could still be useful, I had to define a direction for the nodes in the graph, so I defined a 127x5 grid where get_next_nodes()[node][direction % 6] would give me the node the agent would reach if it went in that direction.  Then a rather complex convert function would turn the grid into an adjacency list. Instead of ray casting, the agent could now determine articulation points in the graph. The agent can now fill the area by making the move that results in the least articulation points in the next two moves. This results in a perfect fill of any area.
