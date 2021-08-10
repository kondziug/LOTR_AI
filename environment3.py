from envBase import EnvBase
from numpy.lib.histograms import _histogram_bin_edges_dispatcher
import Game_Model.globals
import numpy as np

class Environment3(EnvBase): ## combined threat + enemies engaged at questing
    def __init__(self):
        super(Environment3, self).__init__()

    def featuresPlanningActor(self):
        hand = self.game.getPlayer().getHand()
        if not len(hand):
            return []
        self.cardsAvailable = []
        resourcesAvailable = self.game.getPlayer().getResourcesBySphere('Spirit')
        for card in hand:
            if card.getCost() <= resourcesAvailable:
                self.cardsAvailable.append(card.getId())
        if not self.cardsAvailable:
            return []
        stagedEnemies = self.game.getBoard().getStagedEnemies()
        state = np.zeros((len(self.cardsAvailable), Game_Model.globals.numberOfAllies + Game_Model.globals.numberOfEnemies + 1)) ## + resources
        for row in range(len(self.cardsAvailable)):
            if stagedEnemies:
                for enemy in stagedEnemies:
                    state[row][enemy.getId() - 3] = 1
            state[row][self.cardsAvailable[row] - 3] = 1
            state[row][-1] = resourcesAvailable
        return state

    def featuresPlanningCritic(self):
        state = np.zeros(Game_Model.globals.numberOfAllies + Game_Model.globals.numberOfEnemies + 1) ## + resources
        hand = self.game.getPlayer().getHand()
        for card in hand:
            state[card.getId() - 3] = 1
        stagedEnemies = self.game.getBoard().getStagedEnemies()
        for enemy in stagedEnemies:
            state[enemy.getId() - 3] = 1
        state[-1] = self.game.getPlayer().getResourcesBySphere('Spirit')
        return state

    def featuresQuestingActor(self): 
        cardsAvailable = self.game.getPlayer().getAllCharacters()
        engagedEnemies = self.game.getBoard().getEnemiesEngaged()
        combinedThreat = self.game.getBoard().getCombinedThreat()
        digits = 3 + Game_Model.globals.numberOfAllies + Game_Model.globals.numberOfEnemies + 1
        state = np.zeros((len(cardsAvailable), digits))
        for row in range(len(cardsAvailable)):
            state[row][cardsAvailable[row].getId()] = 1
            for enemy in engagedEnemies:
                state[row][enemy.getId()] = 1
            state[row][-1] = combinedThreat
        return state

    def featuresQuestingCritic(self): 
        cardsAvailable = self.game.getPlayer().getAllCharacters()
        engagedEnemies = self.game.getBoard().getEnemiesEngaged()
        combinedThreat = self.game.getBoard().getCombinedThreat()
        digits = 3 + Game_Model.globals.numberOfAllies + Game_Model.globals.numberOfEnemies + 1
        state = np.zeros(digits)
        for card in cardsAvailable:
            state[card.getId()] = 1
        for enemy in engagedEnemies:
            state[enemy.getId()] = 1
        state[-1] = combinedThreat
        return state
