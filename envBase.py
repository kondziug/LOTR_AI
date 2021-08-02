from abc import ABC, abstractmethod
from numpy.lib.histograms import _histogram_bin_edges_dispatcher
from Game_Model.board import Board
from Game_Model.player import Player
from Game_Model.game import Game
import Game_Model.globals
import numpy as np

class EnvBase(ABC):
    def __init__(self):
        player = Player(Game_Model.globals.decks['Player Deck'], Game_Model.globals.heroes, 24) ## threat level should be in globals!!!!!!!!!!!!!!!
        board = Board(Game_Model.globals.decks['Quest Deck'], Game_Model.globals.decks['Encounter Deck'])
        self.game = Game(board, player)
        self.game.setupGame()
        self.game.resourcePhase()
        self.cardsAvailable = []
        self.planning_action = None
        self.handIds = []

    @abstractmethod
    def featuresPlanningActor(self):
        pass

    @abstractmethod
    def featuresPlanningCritic(self):
        pass

    @abstractmethod
    def featuresQuestingActor(self):
        pass

    @abstractmethod
    def featuresQuestingCritic(self):
        pass

    def step_planning(self, action):
        cardId = self.cardsAvailable[action]
        if not self.game.planningPhase(cardId):
            print('smth went wrong at planning')
        for i in range(len(self.handIds)):
            if self.handIds[i] == self.cardsAvailable[action]:
                idx = i
        self.planning_action[idx] = 1
        return

    def step_questing(self, action):
        if len(action) == 1:
            action = np.squeeze(action, axis=0)
        else:
            action = np.squeeze(action)
        cardsAvailable = self.game.getPlayer().getAllCharacters()
        cardList = []
        for i in range(len(action)):
            if action[i]:
                cardList.append(cardsAvailable[i])
        if not cardList:
            return self.featuresQuestingCritic(), -1, True
        combinedWillpower = self.game.getPlayer().setCardsForQuesting(cardList)
        self.game.resolveQuesting(combinedWillpower)
        if Game_Model.globals.gameWin:
            return self.featuresQuestingCritic(), 1, True
        if Game_Model.globals.gameOver:
            return self.featuresQuestingCritic(), -1, True
        return self.featuresQuestingCritic(), 0, False

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
        self.updateHand()
        self.planning_action = np.zeros(len(self.handIds))

    def updateHand(self):
        self.handIds = [] ## only resource affordable
        hand = self.game.getPlayer().getHand()
        if not len(hand):
            return []
        resourcesAvailable = self.game.getPlayer().getResourcesBySphere('Spirit')
        for card in hand:
            if card.getCost() <= resourcesAvailable:
                self.handIds.append(card.getId())

    def reset(self):
        self.game.reset()
        self.game.setupGame()
        self.game.resourcePhase()
        Game_Model.globals.gameWin = False
        Game_Model.globals.gameOver = False
        self.cardsAvailable = []
        self.updateHand()
        self.planning_action = np.zeros(len(self.handIds))
        return self.featuresPlanningCritic()

    def hardReset(self):
        self.game.getBoard().hardReset()
        self.game.getPlayer().hardReset()
