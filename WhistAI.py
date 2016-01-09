from __future__ import print_function
import random

class WhistAI:
    """ Artificial Intelligence for a Whist game (Israeli version) 
    Based on:
        http://en.wikipedia.org/wiki/High_card_points
    
    """
    
    valueToStr = {2:'2',3:'3',4:'4',5:'5',6:'6',7:'7',8:'8',9:'9',10:'10',11:'J',12:'Q',13:'K',14:'A'}
    strToValue = dict(zip(valueToStr.values(),valueToStr.keys()))
    availabeSuits = ('c','d','h','s')
    
    def __init__(self, level = 1, playerNum=0, ownCards=[]):
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
        self.takes = [] # the other people takes

    def setCardsPlayed(self, cardsNames):
        self.cardsPlayed = cardsNames
        print(self.cardsPlayed)
        
    def bid(self, forcedTrump=None, notAlowedBid=None):
        """ Convert total score to bid """
        if forcedTrump is None: #if trump is unknown, check all options and 
                                      #selects the best trump which will maximize the total score
            # collect all scores, for no trump and with trump        
            scores = [self.handEvaluation(selectedTrump=None)]
            for trumpIter in self.availabeSuits:
                scores.append(self.handEvaluation(selectedTrump=trumpIter))
    
            # select highest score            
            ind = scores.index(max(scores))
            if ind == 0:
                selectedTrump = 'notrump'
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
            
        print("Total Score = %d. Selected Trump = %s " % (totalScore,selectedTrump), end='')
        
        # convert score to bid
        if totalScore <= 5:
            bid = 0
        if totalScore >= 6  and totalScore <= 9:
            bid = 1       
        if totalScore >= 10 and totalScore <= 12:
            bid = 2       
        if totalScore >= 13 and totalScore <= 15:
            bid = 3
        if totalScore >= 16 and totalScore <= 18:
            bid = 4
        if totalScore >= 19 and totalScore <= 21:
            bid = 5    
        if totalScore >= 22 and totalScore <= 24:
            bid = 6
        if totalScore >= 25 and totalScore <= 27:
            bid = 7
        if totalScore >= 28 and totalScore <= 30:
            bid = 8
        if totalScore >= 31 and totalScore <= 32:
            bid = 9
        if totalScore >= 33 and totalScore <= 34:
            bid = 10
        if totalScore >= 35 and totalScore <= 36:
            bid = 11            
        if totalScore >= 37 and totalScore <= 38:
            bid = 12           
        if totalScore >= 39 :
            bid = 13
        
        if notAlowedBid is not None:    # if this player cannot bid this value (probably because the sum of all bids is exactly 13)
            print("bid = %d isn't allowed. " % bid,end="")
            bid -= random.randrange(-1,2,2) # TODO - insert some sense here
            if bid < 0 and notAlowedBid != 0:
                bid = 0
            if bid < 0 and notAlowedBid == 0:
                bid = 1
        print("Selected Bid = %d" % bid)            
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
            
            """ Suit Length Points
            5-card suit = 1 point
            6 card suit = 2 points
            7 card suit = 3 points ... etc.
            """
            LP = 0
            for s in suitsCount:
                if s >= 5: # 5 cards or more from the same suit
                    LP += s-4
            
            """ Suit Short Points       
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
            if selectedTrump is not None and selectedTrump is not 'notrump':
                trumpCount = suitsCount[self.availabeSuits.index(selectedTrump)]
                SP = 0
                if trumpCount==3:
                    SP += suitsCount.count(0)*3 + suitsCount.count(1)*2 + suitsCount.count(2)*1
                if trumpCount>=4:
                    SP += suitsCount.count(0)*5 + suitsCount.count(1)*3 + suitsCount.count(2)*1    
            
            """ Controls Count
            The control count is the sum of the controls where aces are valued 
            as two controls, kings as one control and queens and jacks as zero.
            This control count can be used as "tie-breakers" for hands 
            evaluated as marginal by their HCP count
            """
            #CC = valuesCount[14]*2 + valuesCount[13]*1
            
            """ SUM all scores """
            if selectedTrump == 'notrump': #is selected trump = no trump
                totalScore = HCP
            elif selectedTrump is None:  # before agreement on trump 
                totalScore = HCP + LP
            else:    # after agreement on trump 
                totalScore = HCP + SP
            
        return totalScore       
    
    def playCard(self):        
        #print("AI (Player %d): played Cards - " % (self.playerNum,str(self.cardsPlayed)))
        print("AI (Player %d): Own Hand - %s" % (self.playerNum,str(self.ownCards)))
        if self.level >= 0:
            if self.cardsPlayed[-1] == []: # if no one played yet this round
                print("AI (Player %d): first to play this hand" % self.playerNum)
                i = random.randrange(len(self.ownCards))
                selectedCard = self.ownCards[i]
            else:
               currentRound = self.cardsPlayed[-1]
               leadSuit = currentRound[0].split("_")[0]
               cardsAllowed = []
               for cardName in self.ownCards: # find all the allowed cards
                   if cardName.split("_")[0] == leadSuit:
                       cardsAllowed.append(cardName)               
               if cardsAllowed == []: # if player doesn't have cards from the lead suit
                  print("AI (Player %d): Doesn\'t have lead suit %s" % (self.playerNum,leadSuit))
                  print("AI (Player %d): Allowed Cards - %s" % (self.playerNum,str(self.ownCards)))
                  i = random.randrange(len(self.ownCards))
                  selectedCard = self.ownCards[i] 
               else: # if player has cards from the lead suit
                  print("AI (Player %d): Allowed Cards - %s" % (self.playerNum,str(cardsAllowed)))
                  i = random.randrange(len(cardsAllowed))
                  selectedCard = cardsAllowed[i]         
        print("AI (Player %d): selectedCard = %s" % (self.playerNum, selectedCard))
        return selectedCard
    
    def removeCardFromOwn(self,cardName):
        """ removes card from ownCards list """
        self.ownCards.pop(self.ownCards.index(cardName))
          
if __name__ == "__main__":
    whistGame = WhistAI(level=1)
    bid = whistGame.bid()
    print(bid)
