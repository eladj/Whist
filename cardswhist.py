# -*- coding: utf-8 -*-
from __future__ import print_function
from PyQt4.QtCore import *
from PyQt4.QtGui  import *
import cardstable
from WhistAI import WhistAI
from bid import BiddingDialog
import random

class BidDialogExtend(BiddingDialog):
    def __init__(self,AI_players, AIlevel, playerToBid):
        super(BidDialogExtend, self).__init__(AI_players, AIlevel, playerToBid)
   
        
class CardTableWidgetWhist(cardstable.cardTableWidget):
    """ extension of CardTableWidget, for a Whist game """
    AIlevel = 1
    animateFlag = True
    
    def __init__(self):
        super(CardTableWidgetWhist, self).__init__()                
        self.DEBUG = 1
        self.newGame()   
        self.animTimer = QTimer()        
        self.animTimer.setInterval(1500)
        self.animTimer.setSingleShot(True)


    def newGame(self,newRound=False):
        """ handles new game and new round """
        if not newRound:
            self.firstPlayerToBid = random.randrange(1,5,1)
            self.totalScore = [0,0,0,0]
        else:
            self.firstPlayerToBid += 1
            if self.firstPlayerToBid == 5:
                self.firstPlayerToBid = 1        
        self.handsArchive = [[]] #buffer to kepp 4 cards which played in hand        
        self.handsNameArchive = [[]] #buffer to kepp 4 cards which played in hand        
        self.trump = None # the trump suit
        self.bids = ['?','?','?','?']
        self.takes = [0,0,0,0]
        self.textPlayers = []
        self.scene.clear() #clears all items from scene (cards&text)        
        self.paintTable()
        self.dealDeck()        
        self.playerAI = [[],
                         WhistAI(level=self.AIlevel, playerNum=2, 
                                 ownCards=[i.name for i in self.getCardsList(player=2)]),
                         WhistAI(level=self.AIlevel, playerNum=3, 
                                 ownCards=[i.name for i in self.getCardsList(player=3)]),
                         WhistAI(level=self.AIlevel, playerNum=4, 
                                 ownCards=[i.name for i in self.getCardsList(player=4)])] #insert AI players        
        #self.playerAI = [[],[],[],[]]
        QTimer.singleShot(100, self.manageGame)


    def manageGame(self):
        """ manage the game
        pass the play for human or AI player
        """
        if self.bids[0] == '?':  #if no bidding was yet set          
            self.manageBidding()
            return
        AI = self.playerAI[self.playerToPlay-1] 
        print("MANGAE GAME CALLED - Player %d" % self.playerToPlay)
        if AI == []: #if it's human player do nothing            
            #TODO - allow user mouse events
            return
        else:
           #TODO - block user mouse events
           # call AI to select card            
           AI.setCardsPlayed(self.handsNameArchive)
           cardToPlay = AI.playCard()           
           # find card item that match that card name
           cardsItems = self.getCardsList()
           cardsNames = [i.name for i in cardsItems]           
           # play this card           
           self.cardPressed(cardsItems[cardsNames.index(cardToPlay)])
           AI.removeCardFromOwn(cardToPlay)
    
        
    def manageBidding(self):
        """ calls the bidding dialog """
        self.bidDlg = BidDialogExtend(self.playerAI, self.AIlevel, 
                                      self.firstPlayerToBid)
        self.bidDlg.finishedBidding.connect(self.postBidding) # when finished call postBidding  
        self.bidDlg.show()


    def postBidding(self):
        """ called after the bidding window closes. """
        print("postBidding")        
        self.bids = self.bidDlg.finalBids
        self.trump= self.bidDlg.finalTrump
        self.playerToPlay = self.bids.index(max(self.bids))+1
        #self.paintScores()
        self.paintTable()
        QTimer.singleShot(200, self.manageGame) 

    
    def cardPressed(self, card):
        """ handles actions after selecting a card to play """
        if card.player is not self.playerToPlay: # makes sure this is this player turn
            return                        
        if not self.checkIfMoveLegal(card):
            print("Illegal move. player %d cannot play %s" % 
                  (card.player, card.name))
            return
        card = self.changeCard(card,faceDown=False) # turn card face up
        self.moveCardToCenter(card)
        self.handsArchive[-1].append(card)
        self.handsNameArchive[-1].append(card.name)
        card.played = True
        if len(self.handsArchive[-1])==4:
            QTimer.singleShot(1000, self.handleEndOfHand)
        else:
            print("cardPressed calling manageGame")            
            if self.playerToPlay == 4:
                self.playerToPlay = 1
            else:
                self.playerToPlay += 1
            if self.playerAI[self.playerToPlay-1] == []: #if next player is human don't wait
                QTimer.singleShot(10, self.manageGame) 
            else: #if next player is AI wait 1 sec
                QTimer.singleShot(1000, self.manageGame) 


    def handleEndOfHand(self):
        """ handles hand of hand (after each player played a card) """
        playerWonHand = self.checkWhoWonHand()
        print("player %d won the hand" % playerWonHand)          
        self.moveCardsToWinner(playerWonHand)
        self.takes[playerWonHand-1] += 1
        self.playerToPlay = playerWonHand #player who won start the next
        #self.paintScores()        
        self.paintTable()
        self.handsArchive.append([])
        self.handsNameArchive.append([])
        if sum(self.takes)==13: # if round is finished
            self.updateTotalScores()
            self.newGame(newRound=True)
        else:
            QTimer.singleShot(10, self.manageGame) # call for manageGame
                    
       
    def paintTable(self):
        """ paint the table graphics 
        updates the text items for players names,bids,scores... 
        """        
        self.sideMargin = 70        
        self.topMargin = 50        
        #pen = QPen("black")
        #brush = QBrush("black")
        w = self.cardWidth*self.defScale
        h = self.cardHeight*self.defScale
        self.handsPosition = (QPointF(self.scene.width()/2-7*30,self.scene.height()-h-self.topMargin),
                              QPointF(self.sideMargin,self.scene.height()/2-h),
                              QPointF(self.scene.width()/2-7*30,self.topMargin),
                              QPointF(self.scene.width()-w-self.sideMargin,self.scene.height()/2-h))
        self.textPosition = (self.handsPosition[0]+QPointF(-240,40),
                             self.handsPosition[1]+QPointF(0,-100),
                             self.handsPosition[2]+QPointF(280,40),
                             self.handsPosition[3]+QPointF(-30,-100))        
        #font =  QFont("Cursive", 18, QFont.Bold)

        if self.textPlayers == []:        
            self.textPlayers = [[],[],[],[]]        
            for n in range(4):
                self.textPlayers[n] = QGraphicsTextItem()
                self.scene.addItem(self.textPlayers[n])
                self.scene.items()[0].setPos(self.textPosition[n])
                #self.textPlayers[n].setFont(font)
            self.textTrump = QGraphicsTextItem()        
            #self.textTrump.setHtml("<font size=8>Trump: %s</font>" % self.trump)
            self.textTrump.setPos(QPointF(0,20))
            self.scene.addItem(self.textTrump)    
        else:
            self.textTrump.setHtml("<font size=4>Trump: %s</font>" % self.trump)
            for n in range(4):            
                htmlText = "<font size=8>Player %d</font><br> \
                            <font size=5>Bids: %s | Takes: %d<br>Score: %d</font>" % \
                            ((n+1),str(self.bids[n]),self.takes[n],self.totalScore[n])
                self.textPlayers[n].setHtml(htmlText)                              

    
    def dealDeck(self):
        """ Creates the card graphics item and position them  """
        d = self.buildDeckList()        
        random.shuffle(d)
        delta = 25        
        for p in range(4):
            n=0
            playerCards = d[p*13:p*13+13]
            playerCards = self.sortCards(playerCards)            
            for card in playerCards: 
                if p % 2 == 0 :
                    delta = QPointF(12, 0)
                else:
                    delta = QPointF(0, 12)
                if p==0:
                    delta = delta*3
                    faceDownFlag = False
                else:
                    faceDownFlag = False #TODO - Change back!!! !!!!!!!!!!!!!!!!!!!!!!!!!!!11
                self.addCard(card, player=p+1, faceDown=faceDownFlag)
                self.getCardsList()[0].setPos(self.handsPosition[p]+
                                              QPointF(delta)*n)
                n+=1
                                
    def mousePressEvent(self, event):
        """ handles what happen when user clicks the mouse """
        pos = event.pos() + QPoint(-10,-10) #cursor correction - don't know why
        item = self.view.itemAt(pos)                
        if isinstance(item,cardstable.CardGraphicsItem):            
            if self.playerAI[item.player-1] == []: # makes sure this is human player            
                self.cardPressed(item)                
        if self.DEBUG > 3:
            print("mousePressEvent: ",end="")
            print(event,end="")
            print(" pos=",end="")
            print(pos)

        
    def moveCardToCenter(self,card):
        """ handles the graphics of moving a selected card to the middle """
        center = QPointF(int(self.scene.width()//2-50),int(self.scene.height()//2-75))
        delta = (QPointF(0,80),QPointF(-80,0),QPointF(0,-80),QPointF(80,0))
        self.anim2 = (QPropertyAnimation(card, "pos"))
        if self.animateFlag:
            if len(self.handsArchive[-1])==4:
                self.anim2.setDuration(150)
            else:
                self.anim2.setDuration(150)
            #anim.setStartValue(self.pos())
            self.anim2.setEndValue(center+delta[card.player-1])            
            self.anim2.start()            
        else:
            card.setPos(center+delta)            
        if self.DEBUG > 3:
            print("Card Played: " + card.name)


    def moveCardsToWinner(self,player):
        """ handles the animation of moving a hand to the winner """
        delta = (QPointF(0,300),QPointF(-300,0),QPointF(0,-300),QPointF(300,0))
        self.anim=[]
        for card in self.handsArchive[-1]:
            self.anim.append(QPropertyAnimation(card, "pos"))
            self.anim[-1].setDuration(300)
            self.anim[-1].setEndValue(self.handsPosition[player-1]+delta[player-1])            
            self.anim[-1].start()
            #QTimer.singleShot(10, self.anim[-1], SLOT("start()"))
            #QObject.connect(self.anim[-1], SIGNAL("finished()"), self.anim[-1], SLOT("deleteLater()"))             
    
        
    def updateTotalScores(self):
        """ handles total score calculation in the end of the round """
        for p in range(4):
            if self.bids[p]==0: #special case of bid=0
                if sum(self.bids) > 13: # "over"
                    if self.takes[p]==0: # success
                        roundScore = 25
                    else:   # failure
                        roundScore = -25 + abs(self.takes[p]-1)*(10)                
                else: # "under"
                    if self.takes[p]==0: # success
                        roundScore = 50
                    else:   # failure
                        roundScore = -50 + abs(self.takes[p]-1)*(10)
            else:   #regular case
                if self.bids[p]==self.takes[p]: # success
                    roundScore = self.bids[p]**2 + 10
                else:   # failure
                    roundScore = abs(self.bids[p] - self.takes[p])*(-10)
            self.totalScore[p] += roundScore   
        self.scene.update()
        if self.DEBUG > 2:
            print("Updating scores: P1=%d, P2=%d, P3=%d, P4=%d" % tuple(self.totalScore))


    def checkIfMoveLegal(self,card):
        """ checks if current move is allowed """
        if len(self.handsArchive[-1]) == 0: #first card always legal
            return True
        else:
            lastPlayerPlayed = self.handsArchive[-1][-1].player #clockwise order of play
            if (card.player!=lastPlayerPlayed+1 and lastPlayerPlayed!=4) \
            or (lastPlayerPlayed==4 and card.player!=1):
                return False
            leadSuit = self.handsArchive[-1][0].getSuit()
            if card.getSuit() != leadSuit: #check if equal to first card's suit
                playerCards = self.getCardsList(player=card.player,notPlayedOnly=True)
                playerCardSuits = [a.getSuit() for a in playerCards]                
                if playerCardSuits.count(leadSuit) == 0: #if player doesn't have that suit 
                    return True
                else:
                    return False
            else:
                return True
        
        
    def checkWhoWonHand(self):
        """ check which player won the hand """
        players = [h.player for h in self.handsArchive[-1]]
        values = [h.getValue() for h in self.handsArchive[-1]]
        suits = [h.getSuit() for h in self.handsArchive[-1]]
        leadSuit = suits[0]
        trumpInds = [i for i, x in enumerate(suits) if x == self.trump]
        if trumpInds==[]: # if no trump was played
            leadSuitInds = [i for i, x in enumerate(suits) if x == leadSuit]
            maxValue = 0
            for i in leadSuitInds: #check only cards that match the first card suit
                if values[i] > maxValue:
                    maxValue = values[i]
                    res = players[i]            
        else:   # if trump card was played
            maxValue = 0
            for i in trumpInds: #check the highest trump
                if values[i] > maxValue:
                    maxValue = values[i]
                    res = players[i]                
        return res

