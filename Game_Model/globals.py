from Game_Model.hero import Hero
from Game_Model.ally import Ally
from Game_Model.quest import Quest
from Game_Model.enemy import Enemy
from Game_Model.land import Land
from Game_Model.quest_deck import QuestDeck
from Game_Model.regular_deck import RegularDeck

def init():
    global gameOver
    global gameWin
    gameOver = False
    gameWin = False

    global difficulty
    difficulty = 'easy'

    global fullGame
    fullGame = False

    global heroes
    global decks
    heroes = []
    decks = {}

    heroes.append(Hero(0, 'Dunhere', 2, 1, 4, 1, 'Spirit', 8))
    heroes.append(Hero(1, 'Eowyn', 1, 1, 3, 4, 'Spirit', 9))
    heroes.append(Hero(2, 'Eleanor', 1, 2, 3, 1, 'Spirit', 7))

    playerDeck = RegularDeck('Player Deck')
    playerDeck.addCard(Ally(3, 'Lorien Guide', 1, 1, 2, 0, 'Spirit', 3))
    playerDeck.addCard(Ally(4, 'Lorien Guide', 1, 1, 2, 0, 'Spirit', 3))
    playerDeck.addCard(Ally(5, 'Lorien Guide', 1, 1, 2, 0, 'Spirit', 3))
    playerDeck.addCard(Ally(6, 'Northern Tracker', 2, 2, 3, 1, 'Spirit', 4))
    playerDeck.addCard(Ally(7, 'Northern Tracker', 2, 2, 3, 1, 'Spirit', 4))
    playerDeck.addCard(Ally(8, 'Northern Tracker', 2, 2, 3, 1, 'Spirit', 4))
    playerDeck.addCard(Ally(9, 'Wandering Took', 1, 1, 2, 1, 'Spirit', 2))
    playerDeck.addCard(Ally(10, 'Wandering Took', 1, 1, 2, 1, 'Spirit', 2))
    playerDeck.addCard(Ally(11, 'Wandering Took', 1, 1, 2, 1, 'Spirit', 2))
    playerDeck.addCard(Ally(12, 'Rider of Rohan', 2, 0, 2, 2, 'Spirit', 3))
    playerDeck.addCard(Ally(13, 'Rider of Rohan', 2, 0, 2, 2, 'Spirit', 3))
    playerDeck.addCard(Ally(14, 'Rider of Rohan', 2, 0, 2, 2, 'Spirit', 3))
    playerDeck.addCard(Ally(15, 'Gandalf', 4, 4, 4, 4, 'Neutral', 5)) ### watch out: change id numbers in player.findGandalfInHand() when messing around!!!!!!!!!!!!!!!!!!
    playerDeck.addCard(Ally(16, 'Gandalf', 4, 4, 4, 4, 'Neutral', 5))
    playerDeck.addCard(Ally(17, 'Gandalf', 4, 4, 4, 4, 'Neutral', 5))
    decks['Player Deck'] = playerDeck

    global numberOfAllies
    numberOfAllies = 15 ## change when messing with ally cards!!!!!!!!

    questDeck = QuestDeck('Passage through Mirkwood')
    questDeck.addCard(Quest(-1, 'Flies and Spiders', 'Passage through Mirkwood', 8))
    if fullGame:
        questDeck.addCard(Quest(-2, 'A fork in the road', 'Passage through Mirkwood', 2))
        questDeck.addCard(Quest(-3, 'Beorns Path', 'Passage through Mirkwood', 10))
    decks['Quest Deck'] = questDeck

    encounterDeck = RegularDeck('Encounter Deck')
    encounterDeck.addCard(Enemy(18, 'Dol Guldur Orcs', 2, 0, 3, 10, 2))
    encounterDeck.addCard(Enemy(19, 'Dol Guldur Orcs', 2, 0, 3, 10, 2))
    encounterDeck.addCard(Enemy(20, 'Dol Guldur Orcs', 2, 0, 3, 10, 2))
    encounterDeck.addCard(Enemy(21, 'Dol Guldur Beastmaster', 3, 1, 5, 35, 2))
    encounterDeck.addCard(Enemy(22, 'Forest Spider', 2, 1, 4, 25, 2))
    encounterDeck.addCard(Enemy(23, 'Forest Spider', 2, 1, 4, 25, 2))
    encounterDeck.addCard(Enemy(24, 'Forest Spider', 2, 1, 4, 25, 2))
    encounterDeck.addCard(Enemy(25, 'Forest Spider', 2, 1, 4, 25, 2))
    encounterDeck.addCard(Enemy(26, 'East Bight Patrol', 3, 1, 2, 5, 3))
    encounterDeck.addCard(Enemy(27, 'Black Forest Bats', 1, 0, 2, 15, 1))
    encounterDeck.addCard(Enemy(28, 'King Spider', 3, 1, 3, 20, 2))
    encounterDeck.addCard(Enemy(29, 'King Spider', 3, 1, 3, 20, 2))
    encounterDeck.addCard(Enemy(30, 'Ungoliants Spawn', 5, 2, 9, 32, 3))

    global numberOfEnemies
    numberOfEnemies = 13 ## change when messing with enemy cards!!!!

    if difficulty == 'hard':
        encounterDeck.addCard(Land(31, 'Necromancers Pass', 3, 2))
        encounterDeck.addCard(Land(32, 'Enchanted Stream', 2, 2))
        encounterDeck.addCard(Land(33, 'Enchanted Stream', 2, 2))
        encounterDeck.addCard(Land(34, 'Old Forest Road', 1, 3))
        encounterDeck.addCard(Land(35, 'Old Forest Road', 1, 3))
        encounterDeck.addCard(Land(36, 'Forest Gate', 2, 4))
        encounterDeck.addCard(Land(37, 'Forest Gate', 2, 4))
        encounterDeck.addCard(Land(38, 'Great Forest Web', 2, 2))
        encounterDeck.addCard(Land(39, 'Great Forest Web', 2, 2))
        encounterDeck.addCard(Land(40, 'Mountains of Mirkwood', 2, 3))
        encounterDeck.addCard(Land(41, 'Mountains of Mirkwood', 2, 3))
        encounterDeck.addCard(Land(42, 'Mountains of Mirkwood', 2, 3))
        global numberOfLands
        numberOfLands = 12 ## the same with lands!!!!!

    decks['Encounter Deck'] = encounterDeck
