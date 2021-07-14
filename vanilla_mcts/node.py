from Game_Model.regular_deck import RegularDeck
from Game_Model.quest_deck import QuestDeck
from Game_Model.board import Board
from Game_Model.player import Player
from Game_Model.game import Game
from Game_Model.ally import Ally
import Game_Model.globals
import random

class Node:
    def __init__(self, game, parent, stage = None, score = 0):
        self.game = game
        self.utility = 0
        self.visits = 0
        self.children = []
        self.parent = parent
        self.stage = stage
        self.score = score

    def getGame(self):
        return self.game

    def getScore(self):
        return self.score

    def setScore(self, score):
        self.score = score

    # def isTerminal(self):
    #     if not self.game.getPlayer().getHeroes() or self.game.getPlayer().getThreat() > 50:
    #         Game_Model.globals.gameOver = True
    #     if self.game.getBoard().getQuestDeck().getCurrentQuest().getPoints() < 0:
    #         Game_Model.globals.gameWin = True

    # def __str__(self):
    #     fullNames = ''
    #     for name in self.cardList:
    #         fullNames += name + ' '
    #     return fullNames

    #############################################################
    def getUtility(self):
        return self.utility

    def getVisits(self):
        return self.visits

    def getChildren(self):
        return self.children

    def getParent(self):
        return self.parent

    def getStage(self):
        return self.stage

    def incrementVisits(self):
        self.visits += 1

    def incrementUtility(self, score):
        self.utility += score

    def addChild(self, node):
        self.children.append(node) # or copy????

    def resetFamily(self):
        self.utility = 0
        self.visits = 0
        self.parent = None
        self.children = []

    # def initData(self, board, player):
    #     self.feedQuestData(board.getQuestDeck().getCardList())
    #     self.feedDeckData('Board', 'encounterDeck', board.getEncounterDeck().getCardList())
    #     self.feedDeckData('Board', 'stagingArea', board.getStagingArea())
    #     self.feedCreatureData('Board', 'engagementArea', board.getEnemiesEngaged())
    #     self.feedActiveLand(board.getActiveLand())
    #     self.feedDeckData('Player', 'playerDeck', player.getPlayerDeck().getCardList())
    #     self.feedHeroData(player.getHeroes())
    #     self.feedDeckData('Player', 'hand', player.getHand())
    #     self.feedCreatureData('Player', 'allies', player.getAllies())
    #     self.data['Player']['threat'] = player.getThreat()
        
    # def feedDeckData(self, owner, name, cardList):
    #     self.data[owner][name] = {}
    #     for card in cardList:
    #         if card.getName() in self.data[owner][name]:
    #             self.data[owner][name][card.getName()] += 1
    #             continue
    #         self.data[owner][name][card.getName()] = 1
    
    # def feedQuestData(self, questList):
    #     self.data['Board']['questDeck'] = {}
    #     for quest in questList:
    #         self.data['Board']['questDeck'][quest.getName()] = quest.getPoints()

    # def feedCreatureData(self, owner, name, cardList):
    #     self.data[owner][name] = {}
    #     for card in cardList:
    #         if not card.getName() in self.data[owner][name]:
    #             self.data[owner][name][card.getName()] = {}
    #         self.data[owner][name][card.getName()]['hitpoints'] = card.getHitpoints()
    #         self.data[owner][name][card.getName()]['isTapped'] = False
    #         if isinstance(card, Ally):
    #             self.data[owner][name][card.getName()]['isTapped'] = card.isTapped()

    # def feedActiveLand(self, land):
    #     self.data['Board']['activeLand'] = {}
    #     if land:
    #         self.data['Board']['activeLand'][land.getName()] = land.getPoints()

    # def feedHeroData(self, heroList):
    #     self.data['Player']['heroes'] = {}
    #     for hero in heroList:
    #         self.data['Player']['heroes'][hero.getName()] = { 'resourcePool' : hero.getResourcePool(), 'hitpoints' : hero.getHitpoints(), 'isTapped' : hero.isTapped() }

    # def createGame(self):
    #     board = self.createBoard()
    #     player = self.createPlayer()
    #     return Game(board, player)

    # def createBoard(self):
    #     questDeck = QuestDeck('Passage through Mirkwood')
    #     for card in self.data['Board']['questDeck']:
    #         questDeck.addCard(Game_Model.globals.dictOfCards[card], 1)
    #         questDeck.setLastQuest(self.data['Board']['questDeck'][card])
    #     encounterDeck = RegularDeck('Encounter Deck')
    #     for card in self.data['Board']['encounterDeck']:
    #         encounterDeck.addCard(Game_Model.globals.dictOfCards[card], self.data['Board']['encounterDeck'][card])
    #     stagingArea = self.createStaticArea('Board', 'stagingArea')
    #     engagementArea = self.createDynamicArea('Board', 'engagementArea')
    #     activeLand = []
    #     if self.data['Board']['activeLand']:
    #         landToAdd = Game_Model.globals.dictOfCards[next(iter(self.data['Board']['activeLand']))].copy()
    #         landToAdd.setPoints(next(iter(self.data['Board']['activeLand'].values())))
    #         activeLand = [ landToAdd ]
    #     return Board(questDeck, encounterDeck, stagingArea, engagementArea, activeLand)

    # def createPlayer(self):
    #     playerDeck = RegularDeck('Player Deck')
    #     for card in self.data['Player']['playerDeck']:
    #         playerDeck.addCard(Game_Model.globals.dictOfCards[card], self.data['Player']['playerDeck'][card])
    #     heroes = []
    #     for card in self.data['Player']['heroes']:
    #         cardToAdd = Game_Model.globals.dictOfCards[card].copy()
    #         cardToAdd.setHitpoints(self.data['Player']['heroes'][card]['hitpoints'])
    #         cardToAdd.setResourcePool(self.data['Player']['heroes'][card]['resourcePool'])
    #         if self.data['Player']['heroes'][card]['isTapped']:
    #             cardToAdd.tap()
    #         heroes.append(cardToAdd)
    #     hand = self.createStaticArea('Player', 'hand')
    #     allies = self.createDynamicArea('Player', 'allies')
    #     return Player(playerDeck, heroes, hand, allies, self.data['Player']['threat'])

    # def createDynamicArea(self, owner, name):
    #     area = []
    #     for card in self.data[owner][name]:
    #         cardToAdd = Game_Model.globals.dictOfCards[card].copy()
    #         cardToAdd.setHitpoints(self.data[owner][name][card]['hitpoints'])
    #         if isinstance(cardToAdd, Ally) and self.data[owner][name][card]['isTapped']:
    #             cardToAdd.tap()
    #         area.append(cardToAdd)                
    #     return area

    # def createStaticArea(self, owner, name):
    #     area = []
    #     for card in self.data[owner][name]:
    #         for _ in range(0, self.data[owner][name][card]):
    #             area.append(Game_Model.globals.dictOfCards[card].copy())
    #     return area
