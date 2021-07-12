from Game_Model.player import Player
from Game_Model.board import Board
from Game_Model.game import Game
import Game_Model.globals
from node import Node
from mcts import MCTS
import copy
import random

class MCTSAgent:
    def __init__(self, mode, playoutBudget, playoutsPerSimulation, level):
        heroes = copy.deepcopy(globals.heroes)
        playerDeck = copy.deepcopy(globals.decks['Player Deck'])
        player = Player(playerDeck, heroes, [], [], 25)
        questDeck = copy.deepcopy(globals.decks['Quest Deck'])
        encounterDeck = copy.deepcopy(globals.decks['Encounter Deck'])
        board = Board(questDeck, encounterDeck, [], [], [])
        if level == 'hard':
            board.scenarioSetup()
        player.shufflePlayerDeck()
        player.drawHand()
        self.rootNode = Node(board, player, None)
        self.mode = mode
        self.playoutBudget = playoutBudget
        self.playoutsPerSimulation = playoutsPerSimulation

    def simulate(self, outputFile):
        while 1:
            if self.simulatePlanning(outputFile):
                break
            if self.simulateQuesting(outputFile):
                break
            if self.simulateDefense(outputFile):
                break
        globals.gameOver = False
        globals.gameWin = False

    def checkIfLoseWin(self, outputFile):
        if globals.gameOver:
            globals.dmode('gameover')
            outputFile.write('l')
            return True
        if globals.gameWin:
            globals.dmode('gameWin')
            outputFile.write('w')
            return True
        return False

    def simulateMCTS(self):
        mcts = MCTS(self.rootNode, self.playoutBudget, self.playoutsPerSimulation)
        self.rootNode = mcts.makeDecision()
        self.rootNode.resetFamily()
        self.rootNode.isTerminal()

    def simulatePlanning(self, outputFile):
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
        return self.checkIfLoseWin(outputFile)

    def simulateQuesting(self, outputFile):
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
        return self.checkIfLoseWin(outputFile)

    def simulateDefense(self, outputFile):
        if self.mode[2] == 'e':
            game = self.rootNode.createGame()
            game.randomTravelPhase()
            game.encounterPhase()
            game.expertDefense()
            game.playoutAttackEnemies()
            game.refreshPhase()
            self.rootNode = Node(game.getBoard(), game.getPlayer(), None, 'Defense')
        elif self.mode[2] == 'r':
            game = self.rootNode.createGame()
            game.randomTravelPhase()
            game.encounterPhase()
            game.randomDefense()
            game.playoutAttackEnemies()
            game.refreshPhase()
            self.rootNode = Node(game.getBoard(), game.getPlayer(), None, 'Defense')
        else:
            self.simulateMCTS()
        return self.checkIfLoseWin(outputFile)