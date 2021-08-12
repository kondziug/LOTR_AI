from envBase import EnvBase
from numpy.lib.histograms import _histogram_bin_edges_dispatcher
import Game_Model.globals
from mainConfig import difficulty
import numpy as np

class Environment1(EnvBase): ## enemies + lands + round at questing
    def __init__(self):
        super(Environment1, self).__init__()

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
        stagedEnemies = self.game.getBoard().getStagedEnemies()
        lands = self.game.getBoard().getAllLands()
        digits = 3 + Game_Model.globals.numberOfAllies + Game_Model.globals.numberOfEnemies + 1 ## heroes + allies + enemies overall + round
        if difficulty == 'hard' or difficulty == 'medium':
            digits += Game_Model.globals.numberOfLands ## + lands over all
        state = np.zeros((len(cardsAvailable), digits)) 
        for row in range(len(cardsAvailable)):
            state[row][cardsAvailable[row].getId()] = 1
            for enemy in stagedEnemies:
                state[row][enemy.getId()] = 1
            if difficulty == 'hard' or difficulty == 'medium':
                for land in lands:
                    state[row][land.getId()] = 1
            state[row][-1] = self.game.getTurnNumber()
        return state

    def featuresQuestingCritic(self):
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
