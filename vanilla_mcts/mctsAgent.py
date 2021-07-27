from Game_Model.player import Player
from Game_Model.board import Board
from Game_Model.game import Game
import Game_Model.globals
from vanilla_mcts.node import Node
from vanilla_mcts.mcts import MCTS
import copy
import random

class MCTSAgent:
    def __init__(self, mode, playoutBudget, playoutsPerSimulation, playoutType):
        heroes = copy.deepcopy(Game_Model.globals.heroes)
        playerDeck = copy.deepcopy(Game_Model.globals.decks['Player Deck'])
        player = Player(playerDeck, heroes, 24) ### threat level should be in globals!!!!!!!!!!!!
        questDeck = copy.deepcopy(Game_Model.globals.decks['Quest Deck'])
        encounterDeck = copy.deepcopy(Game_Model.globals.decks['Encounter Deck'])
        board = Board(questDeck, encounterDeck)
        game = Game(board, player)
        game.setupGame()
        self.rootNode = Node(board, player, None)
        self.mode = mode
        self.playoutBudget = playoutBudget
        self.playoutsPerSimulation = playoutsPerSimulation
        self.playoutType = playoutType

    def simulate(self):
        while 1:
            if self.simulatePlanning():
                break
            if self.simulateQuesting():
                break
            if self.simulateDefense():
                break
        if Game_Model.globals.gameWin:
            reward = 1
        if Game_Model.globals.gameOver:
            reward = 0
        Game_Model.globals.gameOver = False
        Game_Model.globals.gameWin = False
        return reward

    def checkIfLoseWin(self):
        if Game_Model.globals.gameOver or Game_Model.globals.gameWin:
            return True
        return False

    def simulateMCTS(self):
        mcts = MCTS(self.rootNode, self.playoutBudget, self.playoutsPerSimulation, self.playoutType)
        self.rootNode = mcts.makeDecision()
        self.rootNode.resetFamily()
        self.rootNode.isTerminal()

    def simulatePlanning(self):
        if self.mode[0] == 'e':
            game = self.rootNode.createGame()
            game.resourcePhase()
            game.expertPlanning()
            self.rootNode = Node(game.getBoard(), game.getPlayer(), None, 'Planning')
        elif self.mode[0] == 'r':
            game = self.rootNode.createGame()
            game.resourcePhase()
            game.randomPlanning()
            self.rootNode = Node(game.getBoard(), game.getPlayer(), None, 'Planning')
        else:
            self.simulateMCTS()
        return self.checkIfLoseWin()

    def simulateQuesting(self):
        if self.mode[1] == 'e':
            game = self.rootNode.createGame()
            game.expertQuesting()
            self.rootNode = Node(game.getBoard(), game.getPlayer(), None, 'Questing')
        elif self.mode[1] == 'r':
            game = self.rootNode.createGame()
            game.randomQuesting()
            self.rootNode = Node(game.getBoard(), game.getPlayer(), None, 'Questing')
        else:
            self.simulateMCTS()
        return self.checkIfLoseWin()

    def simulateTravelPhase(self, game):
        if self.mode[2] == 'e':
            game.expertTravelPhase()
        else:
            game.randomTravelPhase()

    def simulateDefense(self):
        if self.mode[3] == 'e':
            game = self.rootNode.createGame()
            self.simulateTravelPhase(game)
            game.encounterPhase()
            game.expertDefense()
            self.simulateAttack(game)
            game.refreshPhase()
            self.rootNode = Node(game.getBoard(), game.getPlayer(), None, 'Defense')
        elif self.mode[3] == 'r':
            game = self.rootNode.createGame()
            self.simulateTravelPhase(game)
            game.encounterPhase()
            game.randomDefense()
            self.simulateAttack(game)
            game.refreshPhase()
            self.rootNode = Node(game.getBoard(), game.getPlayer(), None, 'Defense')
        else:
            self.simulateMCTS()
        return self.checkIfLoseWin()

    def simulateAttack(self, game):
        if self.mode[4] == 'e':
            game.expertAttack()
        else:
            game.randomAttack()