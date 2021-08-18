import numpy as np
from abc import ABC, abstractmethod
import Game_Model.globals

class BaseEncoder(ABC):
    def __init__(self, game):
        self.game = game

    def createRowPlanning(self):
        row = np.zeros(Game_Model.globals.numberOfAllies + Game_Model.globals.numberOfEnemies + 1) ## + resources
        hand = self.game.getPlayer().getHand()
        for card in hand:
            row[card.getId() - 3] = 1
        stagedEnemies = self.game.getBoard().getStagedEnemies()
        for enemy in stagedEnemies:
            row[enemy.getId() - 3] = 1
        row[-1] = self.game.getPlayer().getResourcesBySphere('Spirit')
        return row

    @abstractmethod
    def createRowQuesting(self):
        pass

    def encodePlanning(self, type): ## actor, critic, macro
        if type == 'critic' or type == 'macro':
            return self.createRowPlanning()
        else:
            cardsAvailable = self.filterCards()
            if not cardsAvailable:
                return []
            resourcesAvailable = self.game.getPlayer().getResourcesBySphere('Spirit')
            stagedEnemies = self.game.getBoard().getStagedEnemies()
            state = np.zeros((len(cardsAvailable), Game_Model.globals.numberOfAllies + Game_Model.globals.numberOfEnemies + 1)) ## + resources
            for row in range(len(cardsAvailable)):
                if stagedEnemies:
                    for enemy in stagedEnemies:
                        state[row][enemy.getId() - 3] = 1
                state[row][cardsAvailable[row] - 3] = 1
                state[row][-1] = resourcesAvailable
            return state

    def encodeQuesting(self, type): ## +args
        if type == 'critic' or type == 'macro':
            return self.createRowQuesting()
        else:
            row = self.createRowQuesting()
            cardsAvailable = self.game.getPlayer().getAllCharacters()
            state = np.repeat(row[np.newaxis, :], len(cardsAvailable), 0)
            for i in range(len(cardsAvailable)):
                for card in cardsAvailable:
                    if cardsAvailable[i].getId() == card.getId():
                        continue
                    state[i][card.getId()] = 0
            return state

    def filterCards(self):
        hand = self.game.getPlayer().getHand()
        if not len(hand):
            return []
        cardsAvailable = []
        resourcesAvailable = self.game.getPlayer().getResourcesBySphere('Spirit')
        for card in hand:
            if card.getCost() <= resourcesAvailable:
                cardsAvailable.append(card.getId())
        return cardsAvailable
