from __future__ import print_function
import random

class WhistAI:
    """ Artificial Intelligence for a Whist game (Israeli version) 
    Based on:
        http://en.wikipedia.org/wiki/High_card_points
    
    """
    DEBUG = 2
    valueToStr = {2:'2',3:'3',4:'4',5:'5',6:'6',7:'7',8:'8',9:'9',10:'10',11:'J',12:'Q',13:'K',14:'A'}
    strToValue = dict(zip(valueToStr.values(),valueToStr.keys()))
    availabeSuits = ('c','d','h','s')
    
    def __init__(self, level = 1, playerNum=0, ownCards=[], trump=[]):
        """ Level of AI:
                0 - random
                1 - simple
                2 - advanced
        """        
        self.level = level
        self.playerNum = playerNum
        #self.ownCards = ['d_2','d_3','s_7','c_K','c_A','d_K','d_A','h_6','h_10','s_J','s_5','s_8','s_5'] # own AI player cards
        #self.ownCards = ['c_2','c_3','c_5','d_2','d_4','d_J','h_7','h_9','h_J','s_3','s_5','s_8','s_10'] # own AI player cards        
        self.ownCards = ownCards
        self.noTrumpBidAllowed = True #does no trump bid is allowed?
        self.cardsPlayed = [] #all the cards which were played
        self.bids = []  # the other people bids
        self.takes = [0,0,0,0] # the other people takes
        self.trump = trump

    def setCardsPlayed(self, cardsNames):
        self.cardsPlayed = cardsNames
        
        
    def bid(self, forcedTrump=None, notAlowedBid=None):
        """ Convert total score to bid """
        if forcedTrump is None: #if trump is unknown, check all options and 
                                      #selects the best trump which will maximize the total score
            # collect all scores, for no trump and with trump                                
            scores = []
            for trumpIter in ('nt',) + self.availabeSuits:
                scores.append(self.handEvaluation(selectedTrump=trumpIter))
                if self.DEBUG > 0:
                    print("AI>bid: score for trump=%s is %d" %(trumpIter,scores[-1]))
    
            # select highest score            
            ind = scores.index(max(scores))
            if ind == 0:
                selectedTrump = 'nt'
            else:
                selectedTrump = self.availabeSuits[ind-1]
                
            if not(self.noTrumpBidAllowed) and ind == 0: #if notrump bid isn't allowed and selected
                scores.pop(0)
                ind = scores.index(max(scores))
                selectedTrump = self.availabeSuits[ind]
            totalScore = scores[ind]    
        else:
            totalScore = self.handEvaluation(selectedTrump=forcedTrump)   
            selectedTrump=forcedTrump        
        
        # convert score to bid
        if totalScore == 0:
            bid = 0
        if totalScore >= 1  and totalScore <= 5:
            bid = 1       
        if totalScore >= 6 and totalScore <= 9:
            bid = 2       
        if totalScore >= 10 and totalScore <= 14:
            bid = 3
        if totalScore >= 15 and totalScore <= 18:
            bid = 4
        if totalScore >= 19 and totalScore <= 21:
            bid = 5    
        if totalScore >= 22 and totalScore <= 23:
            bid = 6
        if totalScore >= 24 and totalScore <= 27:
            bid = 7
        if totalScore >= 28 and totalScore <= 31:
            bid = 8
        if totalScore >= 32 and totalScore <= 34:
            bid = 9
        if totalScore >= 35 and totalScore <= 36:
            bid = 10
        if totalScore >= 37 and totalScore <= 37:
            bid = 11            
        if totalScore >= 38 and totalScore <= 38:
            bid = 12           
        if totalScore >= 39 and totalScore <= 90:
            bid = 13
        if totalScore == 1000: # 0 bid
            bid = 0
        
        if notAlowedBid is not None:    # if this player cannot bid this value (probably because the sum of all bids is exactly 13)
            print("bid = %d isn't allowed. " % bid,end="")
            bid -= random.randrange(-1,2,2) # TODO - insert some sense here
            if bid < 0 and notAlowedBid != 0:
                bid = 0
            if bid < 0 and notAlowedBid == 0:
                bid = 1
        if self.DEBUG > 0:    
            print("AI>bid: (P%d) Selected Trump = %s, Selected Bid = %d" %
                  (self.playerNum, selectedTrump,bid))
        return bid, selectedTrump
            
            
    def handEvaluation(self, selectedTrump=None):
        """ Evaluates the initial bidding (no trump)
        and the secondary (with trump selected).
        Summary:
            When intending to make a bid in a suit and there is no agreed upon
            trump suit, add high card points (HCP) and length points (LP) to
            get the total point value of one's hand.
            With an agreed trump suit, add high card points and shortness
            points (SP) instead.
            When making a bid in notrump with intent to play, value high-card 
            points only.
        """
            
        if self.level==0:
            return random.randrange(1,14,1)
            
        if self.level >= 1:
            suits = [r.split("_")[0] for r in self.ownCards]
            values = [self.strToValue[r.split("_")[1]] for r in self.ownCards]
            valuesCount = [values.count(i) for i in range(0,15,1)] #number of cards from each value
            suitsCount = [suits.count(s) for s in self.availabeSuits]

            """basic evaluation method assigns values to the top four honour cards as follows:
            ace = 4 HCP
            king = 3 HCP
            queen = 2 HCP
            jack = 1 HCP        
            """
        
            HCP = valuesCount[14]*4 + valuesCount[13]*3 + valuesCount[12]*2 + valuesCount[11]*1 # High Card Points

            #Goren, Charles; Richard Pavlicek
            if valuesCount[14]==0: #if no Aces -> reducing 1 HCP
                HCP -= 1
            if valuesCount[14]==4: #if 4 Aces -> adding 1 HCP
                HCP += 1
            HCP += valuesCount[10]/2 #adjust 10's -> adding 1/2 HCP for each 10
            
            # TODO - deducting one HCP for a singleton king, queen, or jack.
            
            """ LP - Suit Length Points
            gives bonus for suits with many cards
            5-card suit = 1 point
            6 card suit = 2 points
            7 card suit = 3 points ... etc.
            """

            
            """ SP - Suit Short Points       
            When the supporting hand holds three trumps, shortness is valued as follows:
            void = 3 points
            singleton = 2 points
            doubleton = 1 point
            When the supporting hand holds four or more trumps, thereby having
            more spare trumps for ruffing, shortness is valued as follows:
            void = 5 points
            singleton = 3 points
            doubleton = 1 point
            Shortage points are added to HCP to give total points.            
            """            
            if selectedTrump is not None and selectedTrump != 'nt':                
                trumpCount = suitsCount[self.availabeSuits.index(selectedTrump)]
                LP = 0
                if trumpCount >= 5:
                    LP = trumpCount - 4
                SP = 0
                if trumpCount==3:
                    SP += suitsCount.count(0)*3 + suitsCount.count(1)*2 + suitsCount.count(2)*1
                if trumpCount>=4:
                    SP += suitsCount.count(0)*5 + suitsCount.count(1)*3 + suitsCount.count(2)*1    
                if self.DEBUG > 0:
                    print("AI>handEvaluation: LP=%d, SP=%d" %(LP, SP))
            
            """ ZP - Zero Points - Check for very low cards, for zero bid """            
            ZP = valuesCount[2]*4 + valuesCount[3]*3 + valuesCount[4]*2 + valuesCount[5]*1 # very low Card Points, for zero bid
            if selectedTrump is not None and selectedTrump != 'nt':
                if trumpCount > 4: #if more than 4 trump cards, can't bid 0
                    ZP = 0
                
            """ SUM all scores """
            if selectedTrump == 'nt': #is selected trump = no trump
                totalScore = HCP
            else:    # after agreement on trump 
                totalScore = HCP + LP + SP
            
            if ZP > 15 and totalScore < 5: #decide to bid 0            
                if self.DEBUG > 0:
                    print("AI>handEvaluation: ZP = %d > 15 and totalScore < 5, decided to bid 0" % (ZP))
                totalScore = 1000
                
            if self.DEBUG > 0:
                print("AI>handEvaluation: total Score=%d " %(totalScore))
            
        return totalScore       
    
    def playCard(self):               
        listCardsValue = self.cardsOrderByValue()
        cardsOnTable = self.cardsPlayed[-1]         
        cardsAllowed = []        
        if cardsOnTable == []: # if no one played yet this round            
            leadSuit = []            
            cardsAllowed = self.ownCards
            cardsToWin = self.ownCards
            cardsToLose = []
            highestCardOnTable = []
        else:
            leadSuit = cardsOnTable[0].split("_")[0]
            cardsOnTableRelevant = []
            for c in cardsOnTable: # check which cards is relevant (lead suit)
                if c.split("_")[0] == leadSuit or c.split("_")[0] == self.trump:
                    cardsOnTableRelevant.append(c)
            highestCardOnTable = self.highestCard(cardsOnTableRelevant)
            for cardName in self.ownCards: # find all the allowed cards
               if cardName.split("_")[0] == leadSuit:
                   cardsAllowed.append(cardName)
            if cardsAllowed == []: #if no leadSuit, all cards available
                cardsAllowed = self.ownCards
            cardsToWin = []
            cardsToLose = []            
            for c in cardsAllowed: #check which of the cards allowed will win or lose
                print(listCardsValue.index(c)," < ? >", listCardsValue.index(highestCardOnTable))
                if listCardsValue.index(c) > listCardsValue.index(highestCardOnTable):
                    cardsToWin.append(c)
                else:
                    cardsToLose.append(c)
                 
        ownTakes = self.takes[self.playerNum-1]        
        takesMissing = self.bids[self.playerNum-1] - ownTakes
        if self.DEBUG > 0:
            print("takesMissing",takesMissing)
            print("bids",self.bids)
            print("Cards Allowed",cardsAllowed)
            print("highest Card on Table",highestCardOnTable)
            print("Cards to Win",cardsToWin)
            print("Cards to Lose",cardsToLose) 
        
        #print("AI (Player %d): played Cards - " % (self.playerNum,str(self.cardsPlayed)))        
        if self.level == 0:
            if cardsOnTable == []: # if no one played yet this round
                print("AI(P%d)>playCard: first to play this hand" % self.playerNum)
                i = random.randrange(len(self.ownCards))
                selectedCard = self.ownCards[i]
            else:                                    
                i = random.randrange(len(cardsAllowed))
                selectedCard = cardsAllowed[i] 
                print("AI(P%d)>playCard: Allowed Cards - %s" % (self.playerNum,str(cardsAllowed)))
                
        if self.level >= 1: 
            if takesMissing > 0: #try to take                                
                if cardsToWin == []: #if no cards to win
                    selectedCard = self.lowestCard(cardsToLose) #select the lowest card to lose with                    
                else:
                    if len(cardsOnTable)==3: #if final, chose the lowest card that will give win
                        selectedCard = self.lowestCard(cardsToWin)
                    else:
                        selectedCard = self.highestCard(cardsToWin)
            elif takesMissing <= 0: #try to lose with the highest losing card
                if cardsToLose == []: #if no cards to win
                    selectedCard = self.lowestCard(cardsToWin) #select the lowest card to lose with                    
                else:
                    selectedCard = self.highestCard(cardsToLose)

        if self.level >= 2:
            underGameFlag = sum(self.bids) < 13
            if takesMissing > 0: #try to take
                if cardsToWin == []: #if no cards to win
                    selectedCard = self.lowestCard(cardsToLose) #select the lowest card to lose with                    
                else:
                    if len(cardsOnTable)==3: #if final, chose the lowest card that will give win
                        if underGameFlag:
                            selectedCard = self.highestCard(cardsToWin)
                        else:
                            selectedCard = self.lowestCard(cardsToWin)                        
                    else:
                        if underGameFlag:
                            i = random.randrange(len(cardsAllowed))
                            selectedCard = cardsAllowed[i]
                        else:
                            selectedCard = self.highestCard(cardsToWin)

            elif takesMissing <= 0: #try to lose with the highest losing card
                if cardsToLose == []: #if no cards to win
                    selectedCard = self.lowestCard(cardsToWin) #select the lowest card to lose with                    
                else:
                    selectedCard = self.highestCard(cardsToLose)

            
        if self.DEBUG > 0: 
            print("AI(P%d)>playCard: Own Hand - %s" % (self.playerNum,str(self.ownCards)))                  
            print("AI(P%d)>playCard: selectedCard = %s" % (self.playerNum, selectedCard))
        return selectedCard
    
    
    def cardsOrderByValue(self):        
        """ gives a list of all cards by their value (including trump factor) """
        suitsNoTrump = list(self.availabeSuits)
        if self.trump != 'nt':
            suitsNoTrump.remove(self.trump)
        listOut = []
        for rank in self.valueToStr.values(): #iterate all ranks
            for suit in suitsNoTrump:
                listOut.append(suit + "_" + rank)
        if self.trump != 'nt':
            for rank in self.valueToStr.values(): #iterate all ranks            
                listOut.append(self.trump + "_" + rank)
        return listOut   

    def lowestCard(self,cardsList):
        """ returns the index of the highest card (including trump factor) """
        cardsByValue = self.cardsOrderByValue()
        minInd = len(cardsByValue)
        lowestCard = cardsList[0]
        for c in cardsList:
            if cardsByValue.index(c) < minInd:
                minInd = cardsByValue.index(c)
                lowestCard = c
        return lowestCard
    
    def highestCard(self,cardsList):
        """ returns the index of the highest card (including trump factor) """
        cardsByValue = self.cardsOrderByValue()
        maxInd = 0
        highestCard = cardsList[0]
        for c in cardsList:
            if cardsByValue.index(c) > maxInd:
                maxInd = cardsByValue.index(c)
                highestCard = c
        return highestCard
    
    def cards2SuitAndValue(self,cardsList):
        suits = []
        values = []
        for card in cardsList:
            suits.append(card.split("_")[0])
            values.append(self.strToValue[card.split("_")[1]])
        return suits, values
    
    def removeCardFromOwn(self,cardName):
        """ removes card from ownCards list """
        self.ownCards.pop(self.ownCards.index(cardName))

          
if __name__ == "__main__":
    whistGame = WhistAI(level=1)
    bid = whistGame.bid()
    print(bid)
