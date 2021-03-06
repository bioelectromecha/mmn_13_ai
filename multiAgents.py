# multiAgents.py
# --------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from util import manhattanDistance
import random, util, sys

from game import Agent


class ReflexAgent(Agent):
    """
      A reflex agent chooses an action at each choice point by examining
      its alternatives via a state evaluation function.
  
      The code below is provided as a guide.  You are welcome to change
      it in any way you see fit, so long as you don't touch our method
      headers.
    """

    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.
    
        getAction chooses among the best options according to the evaluation function.
    
        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {North, South, West, East, Stop}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices)  # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.
    
        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.
    
        The code below extracts some useful information from the state, like the
        remaining food (oldFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.
    
        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generateSuccessor(0, action)
        newPos = successorGameState.getPacmanPosition()
        oldFood = currentGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        "*** YOUR CODE HERE ***"
        score = 0
        foodPosList = oldFood.asList()
        # get the manhattan distance to the closest food pellet
        minDistToFood = min(map(lambda x: manhattanDistance(newPos, x), foodPosList))
        # encourage getting closer to food
        score -= minDistToFood
        for state in newGhostStates:
            dist = manhattanDistance(state.getPosition(), newPos)
            # discourage getting too close to a ghost
            if dist < 3:
                score -= int(
                    sys.maxint / (dist + len(newGhostStates) + 1))  # divide also by length to avoid exceeding maxint
                # else: do nothing. If the nearest ghost is farther away than a few steps, pacman shouldn't care
        return score


def scoreEvaluationFunction(currentGameState):
    """
      This default evaluation function just returns the score of the state.
      The score is the same one displayed in the Pacman GUI.
  
      This evaluation function is meant for use with adversarial search agents
      (not reflex agents).
    """
    return currentGameState.getScore()


class MultiAgentSearchAgent(Agent):
    """
      This class provides some common elements to all of your
      multi-agent searchers.  Any methods defined here will be available
      to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.
  
      You *do not* need to make any changes here, but you can if you want to
      add functionality to all your adversarial search agents.  Please do not
      remove anything, however.
  
      Note: this is an abstract class: one that should not be instantiated.  It's
      only partially specified, and designed to be extended.  Agent (game.py)
      is another abstract class.
    """

    def __init__(self, evalFn='scoreEvaluationFunction', depth='2'):
        self.index = 0  # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)


class MinimaxAgent(MultiAgentSearchAgent):
    """
      Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action from the current gameState using self.depth
          and self.evaluationFunction.
    
          Here are some method calls that might be useful when implementing minimax.
    
          gameState.getLegalActions(agentIndex):
            Returns a list of legal actions for an agent
            agentIndex=0 means Pacman, ghosts are >= 1
    
          Directions.STOP:
            The stop direction, which is always legal
    
          gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action
    
          gameState.getNumAgents():
            Returns the total number of agents in the game
        """
        "*** YOUR CODE HERE ***"

        # all actions except 'stop'
        pacmanActions = self.excludeStop(gameState.getLegalActions())

        maxActionVal = -sys.maxint
        bestAction = None
        # find the action with the max value
        for action in pacmanActions:
            curActionVal = self.minValue(gameState.generateSuccessor(0, action), self.depth, 1)
            if maxActionVal < curActionVal:  # a better action was found
                maxActionVal = curActionVal
                bestAction = action
        return bestAction

    def minValue(self, gameState, depth, ghostIndex):
        """ returns the worst evaluation """
        # terminal check
        if gameState.isLose() or gameState.isWin():
            return self.evaluationFunction(gameState)

        # it's pacman's turn
        if ghostIndex == gameState.getNumAgents():
            return self.maxValue(gameState, depth - 1)

        ghostActions = self.excludeStop(gameState.getLegalActions(ghostIndex))

        minActionVal = sys.maxint
        # find the lowest cost outcome out of all ai moves
        for action in ghostActions:
            minActionVal = min(minActionVal,
                               self.minValue(gameState.generateSuccessor(ghostIndex, action), depth, ghostIndex + 1))
        return minActionVal

    def maxValue(self, gameState, depth):
        """ returns the best evaluation """
        # terminal check
        if depth == 0 or gameState.isLose() or gameState.isWin():
            return self.evaluationFunction(gameState)

        pacmanActions = self.excludeStop(gameState.getLegalActions())

        maxActionVal = -sys.maxint
        # find the best cost outcome out of all pacman moves
        for action in pacmanActions:
            maxActionVal = max(maxActionVal, self.minValue(gameState.generateSuccessor(0, action), depth, 1))
        return maxActionVal

    def excludeStop(self, actions):
        try:
            actions.remove('Stop')  # every action except 'Stop'
        except ValueError:
            pass  # do nothing if stop is not there
        return actions


################################################################################################################################################
################################################################################################################################################
################################################################################################################################################

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        # all actions except 'stop'
        pacmanActions = self.excludeStop(gameState.getLegalActions())
        actionDict = dict()
        maxActionVal = self.maxValue(gameState, self.depth , -sys.maxint, sys.maxint, actionDict)
        return actionDict.get(maxActionVal,None)

    def minValue(self, gameState, depth, ghostIndex, alpha, beta, actionDict):
        """ returns the worst evaluation """
        # terminal check
        if gameState.isLose() or gameState.isWin():
            return self.evaluationFunction(gameState)

        # it's pacman's turn
        if ghostIndex == gameState.getNumAgents():
            return self.maxValue(gameState, depth - 1, alpha, beta, actionDict)

        ghostActions = self.excludeStop(gameState.getLegalActions(ghostIndex))

        minActionVal = sys.maxint
        # find the lowest cost outcome out of all ai moves
        for action in ghostActions:
            minActionVal = min(minActionVal,
                               self.minValue(gameState.generateSuccessor(ghostIndex, action), depth, ghostIndex + 1,
                                             alpha, beta, actionDict))
            # prune
            if alpha >= minActionVal: break
            # new beta
            beta = min(beta, minActionVal)
        return minActionVal

    def maxValue(self, gameState, depth, alpha, beta, actionDict):
        """ returns the best evaluation """
        # terminal check
        if depth == 0 or gameState.isLose() or gameState.isWin():
            return self.evaluationFunction(gameState)

        pacmanActions = self.excludeStop(gameState.getLegalActions())

        maxActionVal = -sys.maxint
        # find the best cost outcome out of all pacman moves
        for action in pacmanActions:
            curVal = self.minValue(gameState.generateSuccessor(0, action), depth, 1, alpha, beta, actionDict)
            actionDict[curVal] = action
            maxActionVal = max(maxActionVal, curVal)
            # prune
            if maxActionVal >= beta: break
            # new alpha
            alpha = max(alpha, maxActionVal)
        return maxActionVal

    def excludeStop(self, actions):
        try:
            actions.remove('Stop')  # every action except 'Stop'
        except ValueError:
            pass  # do nothing if stop is not there
        return actions


class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
          Returns the expectimax action using self.depth and self.evaluationFunction
    
          All ghosts should be modeled as choosing uniformly at random from their
          legal moves.
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()


def betterEvaluationFunction(currentGameState):
    """
      Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
      evaluation function (question 5).
  
      DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()


# Abbreviation
better = betterEvaluationFunction


class ContestAgent(MultiAgentSearchAgent):
    """
      Your agent for the mini-contest
    """

    def getAction(self, gameState):
        """
          Returns an action.  You can use any method you want and search to any depth you want.
          Just remember that the mini-contest is timed, so you have to trade off speed and computation.
    
          Ghosts don't behave randomly anymore, but they aren't perfect either -- they'll usually
          just make a beeline straight towards Pacman (or away from him if they're scared!)
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()
