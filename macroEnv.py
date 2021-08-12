from numpy.lib.histograms import _histogram_bin_edges_dispatcher
from Game_Model.board import Board
from Game_Model.player import Player
from Game_Model.game import Game
import Game_Model.globals
from mainConfig import difficulty
import numpy as np

class MacroEnv():
    def __init__(self):
        player = Player(Game_Model.globals.decks['Player Deck'], Game_Model.globals.heroes, 24) ## threat level should be in globals!!!!!!!!!!!!!!!
        board = Board(Game_Model.globals.decks['Quest Deck'], Game_Model.globals.decks['Encounter Deck'])
        self.game = Game(board, player)
        self.game.setupGame()
        self.game.resourcePhase()
        self.cardsAvailable = []
        self.planning_action = None
        self.handIds = []

    def featuresPlanning(self):
        state = np.zeros(Game_Model.globals.numberOfAllies + Game_Model.globals.numberOfEnemies + 1) ## + resources
        hand = self.game.getPlayer().getHand()
        for card in hand:
            state[card.getId() - 3] = 1
        stagedEnemies = self.game.getBoard().getStagedEnemies()
        for enemy in stagedEnemies:
            state[enemy.getId() - 3] = 1
        state[-1] = self.game.getPlayer().getResourcesBySphere('Spirit')
        return state

    def featuresQuesting(self):
        cardsAvailable = self.game.getPlayer().getAllCharacters()
        stagedEnemies = self.game.getBoard().getStagedEnemies()
        lands = self.game.getBoard().getAllLands()
        digits = 3 + Game_Model.globals.numberOfAllies + Game_Model.globals.numberOfEnemies + 1 ## heroes + allies + enemies overall + round
        if difficulty == 'hard' or difficulty == 'medium':
            digits += Game_Model.globals.numberOfLands ## + lands overall
        state = np.zeros(digits) 
        for card in cardsAvailable:
            state[card.getId()] = 1
        for enemy in stagedEnemies:
            state[enemy.getId()] = 1
        if difficulty == 'hard' or difficulty == 'medium':
            for land in lands:
                state[land.getId()] = 1
        state[-1] = self.game.getTurnNumber()
        return state

    def step_planning(self, action):
        self.game.macroPlanning(action[0])
        return self.featuresPlanning()

    def step_questing(self, action):
        self.game.macroQuesting(action[0])
        return self.featuresQuesting(), 0, False

    def endRound(self, mode):
        if mode[2] == 'e':
            self.game.expertTravelPhase()
        else:
            self.game.randomTravelPhase()
        self.game.encounterPhase()
        if mode[3] == 'e':
            self.game.expertDefense()
        else:
            self.game.randomDefense()
        if mode[4] == 'e':
            self.game.expertAttack()
        else:
            self.game.randomAttack()
        self.game.refreshPhase()
        self.game.resourcePhase()
        # self.updateHand()
        # self.planning_action = np.zeros(len(self.handIds))

    # def updateHand(self):
    #     self.handIds = [] ## only resource affordable
    #     hand = self.game.getPlayer().getHand()
    #     if not len(hand):
    #         return []
    #     resourcesAvailable = self.game.getPlayer().getResourcesBySphere('Spirit')
    #     for card in hand:
    #         if card.getCost() <= resourcesAvailable:
    #             self.handIds.append(card.getId())

    def reset(self):
        self.game.reset()
        self.game.setupGame()
        self.game.resourcePhase()
        Game_Model.globals.gameWin = False
        Game_Model.globals.gameOver = False
        # self.cardsAvailable = []
        # self.updateHand()
        # self.planning_action = np.zeros(len(self.handIds))
        return self.featuresPlanning()

    def hardReset(self):
        self.game.getBoard().hardReset()
        self.game.getPlayer().hardReset()
