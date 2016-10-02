# search.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""

import util
from game import Directions
from util import Stack, Queue


class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return [s, s, w, s, w, w, s, w]


"""
Defines a data structure for holding the graph nodes usefull info
"""


class GraphNode:
    def __init__(self, position, path, priority=0):
        self.position = position
        self.path = path
        self.priority = priority


def depthFirstSearch(problem):
    """
    Search the deepest nodes in the search tree first.

    Your search algorithm needs to return a list of actions that reaches the
    goal. Make sure to implement a graph search algorithm.

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print "Start:", problem.getStartState()
    print "Is the start a goal?", problem.isGoalState(problem.getStartState())
    print "Start's successors:", problem.getSuccessors(problem.getStartState())
    """

    # What will differ from one search to the other is only the date structure used to define the frontier
    # if we use stack, we guarantee that it will go to the leaf nodes first, instead of checking the siblings
    frontier = util.Stack()
    frontier.push(GraphNode(problem.getStartState(), []))
    # the list of visited nodes, only needs to hold info about the position
    visited = []

    while not frontier.isEmpty():
        node = frontier.pop()

        # makes sure we're not revisiting nodes
        if node.position not in visited:
            visited.append(node.position)
            if problem.isGoalState(node.position):
                return node.path

            # unpack values and creates a new node with the direction appended to path and adds this node to the
            # frontier
            for next_pos, next_dir, _ in problem.getSuccessors(node.position):
                if next_pos not in visited:
                    frontier.push(GraphNode(next_pos, node.path + [next_dir]))


def breadthFirstSearch(problem):
    """Search the shallowest nodes in the search tree first."""
    # code below is almost the same as the depthFirst algorithm, this line below is the only thing that differ
    frontier = util.Queue()
    frontier.push(GraphNode(problem.getStartState(), []))
    visited = []

    while not frontier.isEmpty():
        node = frontier.pop()

        if node.position not in visited:
            visited.append(node.position)
            if problem.isGoalState(node.position):
                return node.path

            for next_pos, next_dir, _ in problem.getSuccessors(node.position):
                if next_pos not in visited:
                    frontier.push(GraphNode(next_pos, node.path + [next_dir]))


def uniformCostSearch(problem):
    """Search the node of least total cost first."""
    # using the PriorityQueue from utils to associate a priority to each node
    frontier = util.PriorityQueue()
    # at this point I modified the graphnode to include the cost of the path so far, seems to waste more memory
    frontier.push(GraphNode(problem.getStartState(), []), 0)
    visited = []

    while not frontier.isEmpty():
        node = frontier.pop()

        if node.position not in visited:
            visited.append(node.position)
            if problem.isGoalState(node.position):
                return node.path

            for next_pos, next_dir, next_prio in problem.getSuccessors(node.position):
                if next_pos not in visited:
                    # changes are reflected here
                    frontier.push(GraphNode(next_pos, node.path + [next_dir], node.priority + next_prio),
                                  node.priority + next_prio)


def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0


def aStarSearch(problem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    frontier = util.PriorityQueue()
    frontier.push(GraphNode(problem.getStartState(), []), 0)
    visited = []

    while not frontier.isEmpty():
        node = frontier.pop()

        if node.position not in visited:
            visited.append(node.position)
            if problem.isGoalState(node.position):
                return node.path

            for next_pos, next_dir, next_prio in problem.getSuccessors(node.position):
                if next_pos not in visited:
                    # basically, A* will receive it's priority from a heuristic plus the distance to the node
                    # h(n) = heuristic(next_pos, problem)
                    # g(n) = node.priority + next_prio
                    # f(n) = h(n) + g(n)
                    hn = heuristic(next_pos, problem)
                    gn = node.priority + next_prio
                    fn = hn + gn
                    # the node will only need to hold info about the gn, the hn will be calculated according to pos
                    # this took me an hour to realize
                    frontier.push(GraphNode(next_pos, node.path + [next_dir], gn), fn)

# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
