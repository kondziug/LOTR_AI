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
        self.rootNode = Node(game, None)
        self.mode = mode
        self.playoutBudget = playoutBudget
        self.playoutsPerSimulation = playoutsPerSimulation
        self.playoutType = playoutType

    def simulate(self, outputFile):
        while 1:
            if self.simulatePlanning(outputFile):
                break
            if self.simulateQuesting(outputFile):
                break
            if self.simulateDefense(outputFile):
                break
        Game_Model.globals.gameOver = False
        Game_Model.globals.gameWin = False

    def checkIfLoseWin(self, outputFile):
        if Game_Model.globals.gameOver:
            outputFile.write('l')
            return True
        if Game_Model.globals.gameWin:
            outputFile.write('w')
            return True
        return False

    def simulateMCTS(self):
        mcts = MCTS(self.rootNode, self.playoutBudget, self.playoutsPerSimulation, self.playoutType)
        self.rootNode = mcts.makeDecision()
        self.rootNode.resetFamily()
        # self.rootNode.isTerminal()

    def simulatePlanning(self, outputFile):
        if self.mode[0] == 'e':
            game = self.rootNode.getGame()
            game.resourcePhase()
            game.expertPlanning()
            self.rootNode = Node(game, None, 'Planning')
        elif self.mode[0] == 'r':
            game = self.rootNode.getGame()
            game.resourcePhase()
            game.randomPlanning()
            self.rootNode = Node(game, None, 'Planning')
        else:
            self.simulateMCTS()
        return self.checkIfLoseWin(outputFile)

    def simulateQuesting(self, outputFile):
        if self.mode[1] == 'e':
            game = self.rootNode.getGame()
            game.expertQuesting()
            self.rootNode = Node(game, None, 'Questing')
        elif self.mode[1] == 'r':
            game = self.rootNode.getGame()
            game.randomQuesting()
            self.rootNode = Node(game, None, 'Questing')
        else:
            self.simulateMCTS()
        return self.checkIfLoseWin(outputFile)

    def simulateTravelPhase(self, game):
        if self.mode[2] == 'e':
            game.expertTravelPhase()
        else:
            game.randomTravelPhase()

    def simulateDefense(self, outputFile):
        if self.mode[3] == 'e':
            game = self.rootNode.getGame()
            self.simulateTravelPhase(game)
            game.encounterPhase()
            game.expertDefense()
            self.simulateAttack(game)
            game.refreshPhase()
            self.rootNode = Node(game, None, 'Defense')
        elif self.mode[3] == 'r':
            game = self.rootNode.getGame()
            self.simulateTravelPhase(game)
            game.encounterPhase()
            game.randomDefense()
            self.simulateAttack(game)
            game.refreshPhase()
            self.rootNode = Node(game, None, 'Defense')
        else:
            self.simulateMCTS()
        return self.checkIfLoseWin(outputFile)

    def simulateAttack(self, game):
        if self.mode[4] == 'e':
            game.expertAttack()
        else:
            game.randomAttack()