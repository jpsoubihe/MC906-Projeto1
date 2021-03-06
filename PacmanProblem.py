import functools
import math
import time
from notebook import show_map

import readMaze as rM
from Problem import Problem, UndirectedGraph, show_map
from dfs_for_vis import depth_first_graph_search
from informed_search import astar_search_graph, greedy_best_first_search, uniform_cost_search, \
    best_first_graph_search_for_vis
from notebook import display_visual
from uninformed_search import breadth_first_search
from local_search import hill_climbing_search


class PacmanProblem(Problem):
    def __init__(self, initial, goal, maze=None):
        self.initial = initial
        self.goal = goal
        if maze == None:
            self.maze, self.mazeY, self.mazeX = rM.readMaze()
        else:
            self.maze, self.mazeY, self.mazeX = rM.readMaze(maze)

    # for a given position returns the adjacent positions that are gray paths
    def adjacent(self, position):
        adjacent = []
        # left
        if self.maze[position[0], position[1] - 1] == 2:
            if position[1] - 1 < 0:
                adjacent.append((position[0], self.mazeX - 1))
            else:
                adjacent.append((position[0], position[1] - 1))
        # right
        if position[1] + 1 == self.mazeX and self.maze[position[0], 0] == 2:
            adjacent.append((position[0], 0))
        elif position[1] + 1 < self.mazeX and self.maze[position[0], position[1] + 1] == 2:
            adjacent.append((position[0], position[1] + 1))

        # up
        if self.maze[position[0] - 1, position[1]] == 2:
            if position[0] - 1 < 0:
                adjacent.append((self.mazeY - 1, position[1]))
            else:
                adjacent.append((position[0] - 1, position[1]))
        # down
        if position[0] + 1 == self.mazeY and self.maze[0, position[1]] == 2:
            adjacent.append((0, position[1]))
        elif position[0] + 1 < self.mazeY and self.maze[position[0] + 1, position[1]] == 2:
            adjacent.append((position[0] + 1, position[1]))

        return adjacent

    # returns the possible child states for the given state
    def actions(self, state):
        return self.adjacent(state)

    # the goal is reached if all positions that are reachable through the initial state are in the solution
    # and the first and last positions in the solution are the initial position and goal position
    def goal_test(self, states):    
        return states[-1] == self.goal and states[0] == self.initial

    def result(self, state, action):
        return action

    def path_cost(self, c, position1, action, position2):
        # Se as posicoes n forem adjacentes entao nao ha um caminho direto de pos1 pra pos2
        if abs(position1[0] - position2[0]) > 1 or abs(position1[1] - position2[1]) > 1:
            return math.inf
        return c + 1

    # Retorna uma lista com todas as posicoes alcancaveis a partir da posicao dada, inclusive essa posicao
    def reachable_positions(self, startPosition):
        positions = []
        queue = [startPosition]

        while queue:
            position = queue.pop(0)
            positions.append(position)
            actions = self.adjacent(position)

            for action in actions:
                alreadyVisited = False
                for item in positions:
                    if item == action:
                        alreadyVisited = True
                        break

                if alreadyVisited == False:
                    queue.append(action)

        return set(positions)

    # Diz se uma posicao eh alcancavel a partir de outra (True ou False)
    def reachable(self, position1, position2):
        positions = self.reachable_positions(position1)
        return position2 in positions

    # Cada posicao andada custa 1, porem cada ponto unico recolhido vale 2
    def value(self, states):
        return -1 * len(states) + 2 * len(set(states))

    def h2(self, node):
        return self.euclidean_distance(node.state, self.goal)

    def h(self, node):
        return self.manhattan_distance(node.state, self.goal)

    def g(self, node):
        return node.path_cost

    def euclidean_distance(self, position1, position2):
        if self.reachable(position1, position2) is False:
            return math.inf

        # d = self.reachable_positions(position1)
        #
        # reach = []
        # flag_x = False
        # flag_y = False
        #
        # for i in d:
        #     if i[0] == 0:
        #         d_aux = (self.mazeY - 1, i[1])
        #         if self.reachable(d_aux, self.goal) and d.__contains__((self.mazeY - 1, i[1])):
        #             flag_y = True
        #     if i[1] == 0:
        #         d_aux = (i[0], self.mazeX - 1)
        #         if self.reachable(d_aux, self.goal) and d.__contains__((i[0], self.mazeX - 1)):
        #             flag_x = True


        deltaX1 = (position2[0] - position1[0])**2

        deltaY1 = (position2[1] - position1[1])**2
        return (deltaX1 + deltaY1)**0.5



    # Calcula a distancia entre duas posicoes, valido apenas para posicoes que fazem parte da sol
    @functools.lru_cache(maxsize=4096)
    def manhattan_distance(self, position1, position2, lim=100000):
        if position1 == position2:
            return 0

        # dicicionario com formato { item: [distancia, visitado (0 = nao, 1 = sim)], ... }
        d = dict.fromkeys(self.reachable_positions(position1), [math.inf, 0])
        d[position1] = [0, 0]

        i = 0
        while min({l[1] for l in d.values()}) == 0 and i < lim:
            m = math.inf
            current = None
            for k, v in d.items():
                if v[1] == 0 and v[0] < m:
                    current = k
                    m = v[0]

            d[current] = [m, 1]

            neighbors = self.adjacent(current)
            for neighbor in neighbors:
                if d[neighbor][1] == 0 and m + 1 < d[neighbor][0]:
                    d[neighbor] = [m + 1, 0]
                    if neighbor == position2:
                        return m + 1

            current = None
            i = i + 1

        try:
            return d[position2][0]
        except KeyError:
            return math.inf

    def path(self, position1, position2, lim=100000):
        if position1 == position2:
            return 0, [position1]

        # dicicionario com formato { item: [distancia, visitado (0 = nao, 1 = sim)], ... }
        d = dict.fromkeys(self.reachable_positions(position1), [math.inf, 0, []])
        d[position1] = [0, 0, [position1]]

        i = 0
        while min({l[1] for l in d.values()}) == 0 and i < lim:
            m = math.inf
            current = None
            path = []
            for k, v in d.items():
                if v[1] == 0 and v[0] < m:
                    current = k
                    m = v[0]
                    path = v[2]

            d[current] = [m, 1, path]

            neighbors = self.adjacent(current)
            for neighbor in neighbors:
                if d[neighbor][1] == 0 and m + 1 < d[neighbor][0]:
                    pathCopy = path.copy()
                    pathCopy.append(neighbor)
                    d[neighbor] = [m + 1, 0, pathCopy]
                    if neighbor == position2:
                        return pathCopy

            current = None
            i = i + 1

        try:
            pathCopy
        except:
            return []

# ---------------------------------- PROBLEM INITIALIZATION -----------------------------------------------------
# graph constuction defining the possible states + variable set for executing search algorithms


# ---------------------------------- PROBLEM INITIALIZATION -----------------------------------------------------
# graph constuction defining the possible states + variable set for executing search algorithms

pacman_problem1 = PacmanProblem((1, 1), (8, 11))
pacman_problem2 = PacmanProblem((2, 12), (4, 12))
pacman_problem3 = PacmanProblem((0, 1), (2, 12), "mazes/Maze2")

reachable1 = pacman_problem1.reachable_positions(pacman_problem1.initial)
reachable2 = pacman_problem2.reachable_positions(pacman_problem2.initial)
reachable3 = pacman_problem3.reachable_positions(pacman_problem3.initial)

# Showmap Problem 1
graph1 = dict()
aux1 = {}
for position in reachable1:
    aux1[position] = position
for item in aux1.keys():
    graph1[item] = dict.fromkeys(pacman_problem1.adjacent(aux1[item]), 1)

pacman_map1 = UndirectedGraph(graph1)
pacman_map1.locations = aux1

node_colors1 = {node: 'white' for node in pacman_map1.locations.keys()}
node_positions1 = pacman_map1.locations
node_label_pos1 = {k: [v[0] - 0.25, v[1] - 0.4] for k, v in pacman_map1.locations.items()}
edge_weights1 = {(k, k2): '' for k, v in pacman_map1.graph_dict.items() for k2, v2 in v.items()}

# Showmap Problem 2
graph2 = dict()
aux2 = {}
for position in reachable2:
    aux2[position] = position
for item in aux2.keys():
    graph2[item] = dict.fromkeys(pacman_problem2.adjacent(aux2[item]), 1)

pacman_map2 = UndirectedGraph(graph2)
pacman_map2.locations = aux2

node_colors2 = {node: 'white' for node in pacman_map2.locations.keys()}
node_positions2 = pacman_map2.locations
node_label_pos2 = {k: [v[0] - 0.25, v[1] - 0.4] for k, v in pacman_map1.locations.items()}
edge_weights2 = {(k, k2): '' for k, v in pacman_map2.graph_dict.items() for k2, v2 in v.items()}

# Showmap Problem 3
graph3 = dict()
aux3 = {}
for position in reachable3:
    aux3[position] = position
for item in aux3.keys():
    graph3[item] = dict.fromkeys(pacman_problem3.adjacent(aux3[item]), 1)

pacman_map3 = UndirectedGraph(graph3)
pacman_map3.locations = aux3

node_colors3 = {node: 'white' for node in pacman_map3.locations.keys()}
node_positions3 = pacman_map3.locations
node_label_pos3 = {k: [v[0] - 0.25, v[1] - 0.4] for k, v in pacman_map3.locations.items()}
edge_weights3 = {(k, k2): '' for k, v in pacman_map3.graph_dict.items() for k2, v2 in v.items()}

# ---------------------------------- METHOD CALLS -----------------------------------------------------
# ----------------------------------      A*      -----------------------------------------------------

start = time.time()
iterations, all_node_colors, node = astar_search_graph(pacman_problem1)
end = time.time()
print("time elapsed for problem1 astar_search_graph = " + str(end - start) + 's')
print("iterations = " + str(iterations))
print("positions visited = " + str(len(set([x.state for x in node.path()]))))

# result_node_colors = all_node_colors[-1]
# pacman_graph_data = {
#     'graph_dict': pacman_map1.graph_dict,
#     'node_colors': result_node_colors,
#     'node_positions': node_positions1,
#     'node_label_positions': node_label_pos1,
#     'edge_weights': edge_weights1
#  }
# show_map(pacman_graph_data)

start = time.time()
iterations, all_node_colors, node = astar_search_graph(pacman_problem2)
end = time.time()
print("time elapsed for problem2 astar_search_graph = " + str(end - start) + 's')
print("iterations = " + str(iterations))
print("positions visited = " + str(len(set([x.state for x in node.path()]))))

# result_node_colors = all_node_colors[-1]
# pacman_graph_data = {
#     'graph_dict': pacman_map2.graph_dict,
#     'node_colors': result_node_colors,
#     'node_positions': node_positions2,
#     'node_label_positions': node_label_pos2,
#     'edge_weights': edge_weights2
#  }
# show_map(pacman_graph_data)

start = time.time()
iterations, all_node_colors, node = astar_search_graph(pacman_problem3)
end = time.time()
print("time elapsed for problem3 astar_search_graph = " + str(end - start) + 's')
print("iterations = " + str(iterations))
print("positions visited = " + str(len(set([x.state for x in node.path()]))))

# result_node_colors = all_node_colors[-1]
# pacman_graph_data = {
#     'graph_dict': pacman_map3.graph_dict,
#     'node_colors': result_node_colors,
#     'node_positions': node_positions3,
#     'node_label_positions': node_label_pos3,
#     'edge_weights': edge_weights3
#  }
# show_map(pacman_graph_data)


# ----------------------------------  GREEDY_BEST_FIRST ------------------------------------------------

start = time.time()
iterations, all_node_colors, node = greedy_best_first_search(pacman_problem1, pacman_problem1.h)
end = time.time()
print("time elapsed for problem1 greedy_best_first_search = " + str(end - start) + 's')
print("iterations = " + str(iterations))
print("positions visited = " + str(len(set([x.state for x in node.path()]))))

# result_node_colors = all_node_colors[-1]
# pacman_graph_data = {
#     'graph_dict': pacman_map1.graph_dict,
#     'node_colors': result_node_colors,
#     'node_positions': node_positions1,
#     'node_label_positions': node_label_pos1,
#     'edge_weights': edge_weights1
#  }
# show_map(pacman_graph_data)

start = time.time()
iterations, all_node_colors, node = greedy_best_first_search(pacman_problem2, pacman_problem2.h)
end = time.time()
print("time elapsed for problem2 greedy_best_first_search = " + str(end - start) + 's')
print("iterations = " + str(iterations))
print("positions visited = " + str(len(set([x.state for x in node.path()]))))

# result_node_colors = all_node_colors[-1]
# pacman_graph_data = {
#     'graph_dict': pacman_map2.graph_dict,
#     'node_colors': result_node_colors,
#     'node_positions': node_positions2,
#     'node_label_positions': node_label_pos2,
#     'edge_weights': edge_weights2
#  }
# show_map(pacman_graph_data)

start = time.time()
iterations, all_node_colors, node = greedy_best_first_search(pacman_problem3, pacman_problem3.h)
end = time.time()
print("time elapsed for problem3 greedy_best_first_search = " + str(end - start) + 's')
print("iterations = " + str(iterations))
print("positions visited = " + str(len(set([x.state for x in node.path()]))))

# result_node_colors = all_node_colors[-1]
# pacman_graph_data = {
#     'graph_dict': pacman_map3.graph_dict,
#     'node_colors': result_node_colors,
#     'node_positions': node_positions3,
#     'node_label_positions': node_label_pos3,
#     'edge_weights': edge_weights3
#  }
# show_map(pacman_graph_data)

# ----------------------------------  BREADTH_FIRST  ----------------------------------------------------------

start = time.time()
iterations, all_node_colors, node = breadth_first_search(pacman_problem1)
end = time.time()
print("time elapsed for problem1 breadth_first_tree_search = "+ str(end - start) + 's')
print("iterations = " + str(iterations))
print("positions visited = " + str(len(set([x.state for x in node.path()]))))

# result_node_colors = all_node_colors[-1]
# pacman_graph_data = {
#     'graph_dict': pacman_map1.graph_dict,
#     'node_colors': result_node_colors,
#     'node_positions': node_positions1,
#     'node_label_positions': node_label_pos1,
#     'edge_weights': edge_weights1
#  }
# show_map(pacman_graph_data)

start = time.time()
iterations, all_node_colors, node = breadth_first_search(pacman_problem2)
end = time.time()
print("time elapsed for problem2 breadth_first_tree_search = "+ str(end - start) + 's')
print("iterations = " + str(iterations))
print("positions visited = " + str(len(set([x.state for x in node.path()]))))

# result_node_colors = all_node_colors[-1]
# pacman_graph_data = {
#     'graph_dict': pacman_map2.graph_dict,
#     'node_colors': result_node_colors,
#     'node_positions': node_positions2,
#     'node_label_positions': node_label_pos2,
#     'edge_weights': edge_weights2
#  }
# show_map(pacman_graph_data)

start = time.time()
iterations, all_node_colors, node = breadth_first_search(pacman_problem3)
end = time.time()
print("time elapsed for problem3 breadth_first_tree_search = "+ str(end - start) + 's')
print("iterations = " + str(iterations))
print("positions visited = " + str(len(set([x.state for x in node.path()]))))

# result_node_colors = all_node_colors[-1]
# pacman_graph_data = {
#     'graph_dict': pacman_map3.graph_dict,
#     'node_colors': result_node_colors,
#     'node_positions': node_positions3,
#     'node_label_positions': node_label_pos3,
#     'edge_weights': edge_weights3
#  }
# show_map(pacman_graph_data)


# ----------------------------------  DEPTH_FIRST  ----------------------------------------------------------

start = time.time()
iterations, all_node_colors, node = depth_first_graph_search(pacman_problem1)
end = time.time()
print("time elapsed for problem1 depth_first_graph_search = " + str(end - start) + 's')
print("iterations = " + str(iterations))
print("positions visited = " + str(len(set([x.state for x in node.path()]))))

# result_node_colors = all_node_colors[-1]
# pacman_graph_data = {
#     'graph_dict': pacman_map1.graph_dict,
#     'node_colors': result_node_colors,
#     'node_positions': node_positions1,
#     'node_label_positions': node_label_pos1,
#     'edge_weights': edge_weights1
#  }
# show_map(pacman_graph_data)

start = time.time()
iterations, all_node_colors, node = depth_first_graph_search(pacman_problem2)
end = time.time()
print("time elapsed for problem2 depth_first_graph_search = " + str(end - start) + 's')
print("iterations = " + str(iterations))
print("positions visited = " + str(len(set([x.state for x in node.path()]))))

# result_node_colors = all_node_colors[-1]
# pacman_graph_data = {
#     'graph_dict': pacman_map2.graph_dict,
#     'node_colors': result_node_colors,
#     'node_positions': node_positions2,
#     'node_label_positions': node_label_pos2,
#     'edge_weights': edge_weights2
#  }
# show_map(pacman_graph_data)

start = time.time()
iterations, all_node_colors, node = depth_first_graph_search(pacman_problem3)
end = time.time()
print("time elapsed for problem3 depth_first_graph_search = " + str(end - start) + 's')
print("iterations = " + str(iterations))
print("positions visited = " + str(len(set([x.state for x in node.path()]))))

# result_node_colors = all_node_colors[-1]
# pacman_graph_data = {
#     'graph_dict': pacman_map3.graph_dict,
#     'node_colors': result_node_colors,
#     'node_positions': node_positions3,
#     'node_label_positions': node_label_pos3,
#     'edge_weights': edge_weights3
#  }
# show_map(pacman_graph_data)

# ----------------------------------  HILL_CLIMBING  ----------------------------------------------------------

start = time.time()
iterations, all_node_colors, node = hill_climbing_search(pacman_problem1)
end = time.time()
print("time elapsed for problem1 hill_climbing_search = " + str(end - start) + 's')
print("iterations = " + str(iterations))
print("positions visited = " + str(len(set([x.state for x in node.path()]))))

# result_node_colors = all_node_colors[-1]
# pacman_graph_data = {
#     'graph_dict': pacman_map1.graph_dict,
#     'node_colors': result_node_colors,
#     'node_positions': node_positions1,
#     'node_label_positions': node_label_pos1,
#     'edge_weights': edge_weights1
#  }
# show_map(pacman_graph_data)

start = time.time()
iterations, all_node_colors, node = hill_climbing_search(pacman_problem2)
end = time.time()
print("time elapsed for problem2 hill_climbing = " + str(end - start) + 's')
print("iterations = " + str(iterations))
print("positions visited = " + str(len(set([x.state for x in node.path()]))))

# result_node_colors = all_node_colors[-1]
# pacman_graph_data = {
#     'graph_dict': pacman_map2.graph_dict,
#     'node_colors': result_node_colors,
#     'node_positions': node_positions2,
#     'node_label_positions': node_label_pos2,
#     'edge_weights': edge_weights2
#  }
# show_map(pacman_graph_data)

start = time.time()
iterations, all_node_colors, node = hill_climbing_search(pacman_problem3)
end = time.time()
print("time elapsed for problem3 hill_climbing = " + str(end - start) + 's')
print("iterations = " + str(iterations))
print("positions visited = " + str(len(set([x.state for x in node.path()]))))

# result_node_colors = all_node_colors[-1]
# pacman_graph_data = {
#     'graph_dict': pacman_map3.graph_dict,
#     'node_colors': result_node_colors,
#     'node_positions': node_positions3,
#     'node_label_positions': node_label_pos3,
#     'edge_weights': edge_weights3
#  }
# show_map(pacman_graph_data)

# ----------------------------------  VISUAL_DISPLAY  ----------------------------------------------------------

pacman_graph_data = {
    'graph_dict': pacman_map1.graph_dict,
    'node_colors': node_colors1,
    'node_positions': node_positions1,
    'node_label_positions': node_label_pos1,
    'edge_weights': edge_weights1
 }

#display_visual(pacman_graph_data, True, best_first_graph_search_for_vis, PacmanProblem((1,1), (8,11)))
