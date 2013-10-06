# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui  import *
import cardstable
import random
  
class CardTableWidgetExtend(cardstable.cardTableWidget):
    """ extension of CardTableWidget """
    def __init__(self):
        super(CardTableWidgetExtend, self).__init__()                
        self.DEBUG = 5        
        self.newGame()   
        self.animTimer = QTimer()        
        self.animTimer.setInterval(1500)
        self.animTimer.setSingleShot(True)


    def cardPressed(self, card, position):
        """ handles actions after selecting a card to play """
        if self.checkIfMoveLegal(card):
            self.changeCard(card,faceDown=False)
            card = self.view.itemAt(position)                       
        else:
            print("Illegal move. player %d cannot play %s" % 
                  (card.player, card.name))
            return
        self.moveCardToCenter(card)
        self.currentHand.append(card)
        card.played = True        
        if len(self.currentHand)==4:
            QTimer.singleShot(1500, self.handleEndOfHand)


    def handleEndOfHand(self):
        """ handles hand of hand (after each player played a card) """
        playerWonHand = self.checkWhoWonHand()
        print("player %d won the hand" % playerWonHand)          
        self.moveCardsToWinner(playerWonHand)
        self.takes[playerWonHand-1] += 1
        self.paintScores()
        self.currentHand = []
        if sum(self.takes)==13: # if round is finished
            self.newRound


    def newGame(self):
        self.totalScore = [0,0,0,0]
        self.currentHand = [] #buffer to kepp 4 cards which played in hand        
        self.trump = 's' # the trump suit
        self.bids = [2,2,0,0]
        self.takes = [0,0,0,0]
        self.scene.clear() #clears all items from scene (cards&text)        
        self.paintTable()
        self.dealDeck()
        
    def newRound(self):
        """  """
        self.updateScores()
        self.currentHand = [] #buffer to kepp 4 cards which played in hand        
        self.trump = 's' # the trump suit
        self.bids = [2,2,0,0]
        self.takes = [0,0,0,0]        
        #self.paintScores()
        self.scene.clear() #clears all items from scene (cards&text)        
        self.paintTable()
        self.dealDeck()
       
    
    def paintTable(self):
        """ paint the table graphics """
        self.animateFlag = True
        self.defScale = 0.6
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
        self.textPlayers = [[],[],[],[]]
        for n in range(4):
            self.textPlayers[n] = QGraphicsTextItem()                              
            self.scene.addItem(self.textPlayers[n])
            self.scene.items()[0].setPos(self.textPosition[n])
            #self.textPlayers[n].setFont(font)
        self.paintScores() 

    def paintScores(self):
        """ updates the text items for players names,bids,scores... 
        This method is called from paintTable - don't use it directly!
        """        
        for n in range(4):            
            htmlText = "<font size=8>Player %d</font><br> \
                        <font size=5>Bids: %d | Takes: %d<br>Score: %d</font>" % \
                        ((n+1),self.bids[n],self.takes[n],self.totalScore[n])
            self.textPlayers[n].setHtml(htmlText)                                        

    
    def dealDeck(self):
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
                    faceDownFlag = False #TODO - Change back!!! !!!!!!!!!!!!!!!!!!!!!!!!!!!11
                else:
                    faceDownFlag = False
                self.addCard(card, player=p+1, faceDown=faceDownFlag)
                self.getCardsList()[0].setPos(self.handsPosition[p]+
                                              QPointF(delta)*n)                
                n+=1
                                
    def mousePressEvent(self, event):
        pos = event.pos() + QPoint(-10,-10) #cursor correction - don't know why
        item = self.view.itemAt(pos)                
        if isinstance(item,cardstable.CardGraphicsItem):            
            self.cardPressed(item, pos)        
        if self.DEBUG > 3:
            print("mousePressEvent: ",end="")
            print(event,end="")
            print(" pos=",end="")
            print(pos)
        
    def moveCardToCenter(self,card):
        center = QPointF(int(self.scene.width()//2-50),int(self.scene.height()//2-75))
        delta = (QPointF(0,80),QPointF(-80,0),QPointF(0,-80),QPointF(80,0))
        self.anim2 = (QPropertyAnimation(card, "pos"))
        if self.animateFlag:
            if len(self.currentHand)==4:
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
        delta = (QPointF(0,300),QPointF(-300,0),QPointF(0,-300),QPointF(300,0))
        self.anim=[]
        for card in self.currentHand:
            self.anim.append(QPropertyAnimation(card, "pos"))
            self.anim[-1].setDuration(300)
            self.anim[-1].setEndValue(self.handsPosition[player-1]+delta[player-1])            
            self.anim[-1].start()
            #QTimer.singleShot(10, self.anim[-1], SLOT("start()"))
            #QObject.connect(self.anim[-1], SIGNAL("finished()"), self.anim[-1], SLOT("deleteLater()"))             
    
        
    def updateScores(self):
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
        if len(self.currentHand) == 0: #first card always legal
            return True
        else:
            lastPlayerPlayed = self.currentHand[-1].player #clockwise order of play
            if (card.player!=lastPlayerPlayed+1 and lastPlayerPlayed!=4) \
            or (lastPlayerPlayed==4 and card.player!=1):
                return False
            leadSuit = self.currentHand[0].getSuit()
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
        players = [h.player for h in self.currentHand]
        values = [h.getValue() for h in self.currentHand]
        suits = [h.getSuit() for h in self.currentHand]
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

        
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        # create widgets
        self.cardsTable = CardTableWidgetExtend()        
        menubar = self.menuBar()
        menu = menubar.addMenu('&Main')
        menubar.addMenu('&Help')        
        newGameAction = QAction('&New Game', self)        
        newGameAction.setShortcut('Ctrl+N')
        newGameAction.setStatusTip('Start New Game')
        newGameAction.triggered.connect(self.cardsTable.newGame)
        menu.addAction(newGameAction)        

        
        # main layout
        self.mainLayout = QVBoxLayout()        
        # add all widgets to the main vLayout        
        self.mainLayout.addWidget(self.cardsTable)        
        # central widget
        self.centralWidget = QWidget()
        self.centralWidget.setLayout(self.mainLayout)                
        # set central widget
        self.setCentralWidget(self.centralWidget)
            

        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.setWindowTitle("Israeli Whist")
    widget.setWindowIcon(QIcon('icon.png'))
    widget.setGeometry(QRect(50,50,1024,576))
    widget.show()
    sys.exit(app.exec_())

