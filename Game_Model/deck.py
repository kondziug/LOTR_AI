class Deck:
    def __init__(self, name):
        self.name = name
        self.cardList = []

    def getName(self):
        return self.name

    def getCardList(self):
        return self.cardList

    def takeOffTop(self):
        return self.pullCard(0)

    def pullCard(self, index):
        if len(self.cardList) == 0:
            return None
        card = self.cardList[index]
        self.cardList = self.cardList[:index] + self.cardList[(index+1):]
        return card

    def size(self):
        return len(self.cardList)

    def addCard(self, card):
        self.cardList.append(card)

    def removeCard(self, card):
        self.cardList.remove(card)

    def findCard(self, name):
        for card in self.cardList:
            if card.getName() == name:
                return card

    
