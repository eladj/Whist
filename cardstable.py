from __future__ import print_function
import sys
import os
from PyQt4.QtCore import *
from PyQt4.QtGui  import *
from PyQt4 import QtSvg
import random


class QGraphicsViewExtend(QGraphicsView):
    """ extends QGraphicsView for resize event handling  """
    def __init__(self, parent=None):
        super(QGraphicsViewExtend, self).__init__(parent)               
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    
    def resizeEvent(self, event):
        self.fitInView(QRectF(0,0,1280,720),Qt.KeepAspectRatioByExpanding) #KeepAspectRatioByExpanding ,KeepAspectRatio
        #self.fitInView(QRectF(self.viewport().rect()),Qt.KeepAspectRatio)        

        
class CardGraphicsItem(QtSvg.QGraphicsSvgItem):
    """ Extends QtSvg.QGraphicsSvgItem for card items graphics """ 
    valueToStr = {2:'2',3:'3',4:'4',5:'5',6:'6',7:'7',8:'8',9:'9',10:'10',11:'J',12:'Q',13:'K',14:'A'}
    strToValue = dict (zip(valueToStr.values(),valueToStr.keys()))
    
    def __init__(self, name, ind, svgFile, player=0, faceDown=False, played=False):
        super(CardGraphicsItem, self).__init__(svgFile)
        # special properties
        self.name = name        
        self.ind = ind # index
        self.svgFile = svgFile # svg file for card graphics
        self.player = player # which player holds the card
        self.faceDown = faceDown # does the card faceDown        
        self.played = played
        
        #default properties
        #self.setCursor(Qt.OpenHandCursor)
        self.setAcceptHoverEvents(True) #by Qt default it is set to False        
        self.setAcceptedMouseButtons(Qt.NoButton) #disable mouse events -> they will transfer to the scene                

    def getSuit(self):
        """ get card suit type """    
        return self.name.split("_")[0]
    
    
    def getRank(self):    
        """ get card rank type """        
        return self.name.split("_")[1]
        
    
    def getValue(self):        
        """ return card value in number, by their rank """
        if self.getSuit()=='j':
            return 99     
        return self.strToValue[self.getRank()]


    def setPlayer(self, player):
        """ set player number """
        self.player = player

       
    def hoverEnterEvent(self, event):
        """ event when mouse enter a card """    
        effect = QGraphicsDropShadowEffect(self)
        effect.setBlurRadius(15)
        effect.setColor(Qt.red)        
        effect.setOffset(QPointF(-5,0))
        self.setGraphicsEffect(effect)        
        #self.setCursor(QCursor(Qt.CursorShape(Qt.OpenHandCursor)))
        
    def hoverLeaveEvent(self, event):
        """ event when mouse leave a card """    
        self.setGraphicsEffect(None) 
        #self.setCursor(QCursor(Qt.CursorShape(Qt.ArrowCursor)))
    
    def __repr__(self):                
        return '<CardGraphicsItem: %s>' % self.name
     
        
class cardTableWidget(QWidget):     
    """ main widget for handling the card table """    
    DEBUG = 3 # Debug level    
    svgCardsPath = "svg"
    deckBackSVG = 'back_2'        
    cardWidth = 200 # original card width in pixels
    cardHeight = 250 # original card height in pixels    
    defScale = 0.5  # default scale of card
        
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)       
        self.initUI()

        
    def initUI(self):
        """ initialize the view-scene graphic environment """        
        self.scene = QGraphicsScene()                
        self.view = QGraphicsViewExtend(self.scene)
        self.scene.setSceneRect(QRectF(0,0,1280,720))
        #self.view.setSceneRect(QRectF(self.view.viewport().rect()))
        self.view.setSceneRect(QRectF(0,0,1280,720))
        self.view.setGeometry(QRect(0,0,1280,720))
        self.view.setRenderHint(QPainter.Antialiasing)        
        #self.view.connect(self.a,self.scene.changed())        
        layout = QGridLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)        
        self.setBackgroundColor(QColor('green'))
        
        # special properties
        #self.defInsertionPos = QPointF(0,0)
       
    def getCenterPoint(self)        :
        """ finds screen center point """       
        rect = self.view.geometry()       
        print(rect)
        return QPointF(rect.width()/2,rect.height()/2)       


    def sortCards(self,cards):        
        """ sorting list of card names by suit and value """
        s = sorted(cards, key=lambda c: CardGraphicsItem.strToValue[c.split("_")[1]]) # sort on secondary key
        return sorted(s, key=lambda c: c.split("_")[0]) # now sort on primary key
        
    
    def setBackgroundColor(self, color):
        """ add background color """
        brush = QBrush(color)
        self.scene.setBackgroundBrush(brush)
        self.scene.backgroundBrush() 


    def cardSvgFile(self, name):
        """ get card svg file from card name 
        name = 'c_4','d_Q',...
        for jokers name = 'j_r' or 'j_b'
        for back name = 'back_1', 'back_2', ...
        """
        fn = os.path.join(self.svgCardsPath,name + ".svg")        
        return fn

            
    def addCard(self, name, player=0, faceDown=False, index=None):
        """ adds CardGraphicsItem graphics to board.
        also updates the total cards list
        """        
        # svg file of the card graphics
        if faceDown:
            svgFile = self.cardSvgFile(self.deckBackSVG)            
        else:
            svgFile = self.cardSvgFile(name)
        
        # create CardGraphicsItem instance
        ind = len(self.getCardsList()) + 1
        tmp = CardGraphicsItem(name, ind, svgFile, player, faceDown)        
        tmp.setScale(self.defScale)
        tmp.setZValue(ind) # set ZValue as index (last in is up)        
        self.scene.addItem(tmp)
        if self.DEBUG > 1:
            print("Adding card: ",end="")
            print(tmp,end="")
            print(" index=",ind)


    def removeCard(self, card):
        """ removes CardGraphicsItem graphics from board 
        also removes from the total cards list
        """
        if isinstance(card,int):
            allCards = self.getCardsList()
            indices = [c.ind for c in allCards]
            ind = indices.index(card)            
            self.scene.removeItem(allCards[ind])            
        if isinstance(card,CardGraphicsItem):
            self.scene.removeItem(card)
        if self.DEBUG > 1:
            print("Removing card: ",end="")    
            print(card)
    
    def changeCard(self, cardRemove, nameToAdd=None, faceDown=False):       
        """ replace CardGraphicsItem         
        keeps same index and ZValue !
        if nameToAdd is empty takes the name of the previous (useful for 
        just flipping the card facedown)
        """
        if self.DEBUG > 1:
            print("Changeing card: ",end="")    
            print(cardRemove, end="")
            print(" with card: %s" % nameToAdd, end="")
            print("  faceDown = %r" % faceDown)        
        if isinstance(cardRemove,int):
            #find the card index
            allCards = self.getCardsList()
            indices = [c.ind for c in allCards]
            ind = indices.index(cardRemove)
            cardRemove = allCards[ind]            
        if nameToAdd==None:
            nameToAdd = cardRemove.name

        zValueTmp = cardRemove.zValue()
        positionTmp = cardRemove.pos()
        angleTmp = cardRemove.rotation()
        scaleTmp = cardRemove.scale()
        playerTmp = cardRemove.player
        indTmp= cardRemove.ind
        self.removeCard(cardRemove)
        self.addCard(nameToAdd, playerTmp, faceDown)
        cardsList = self.getCardsList()
        cardsList[0].setZValue(zValueTmp)            
        cardsList[0].setPos(positionTmp)
        cardsList[0].setRotation(angleTmp)
        cardsList[0].setScale(scaleTmp)
        cardsList[0].setPlayer(playerTmp)
        cardsList[0].ind = indTmp
        return cardsList[0] 
            
    def deleteAllCards(self):
        """ removes all cards items from scene
        used to start new round or game
        """ 
        if self.DEBUG > 2:
            print("removing all cards...")
        cards = self.getCardsList()
        for card in cards:
            self.scene.removeItem(card)



    def getCardsList(self,player=None, suit=None, notPlayedOnly=False):
        """ returns and prints all CardGraphicsItem in scene (disregard other graphics items) """        
        itemsOut=[]        
        for item in self.scene.items():
            if isinstance(item,CardGraphicsItem):                
                itemsOut.append(item)
        if player != None:
            playersInds = [i.player for i in itemsOut]
            playerInds = [i for i, x in enumerate(playersInds) if x == player]
            itemsTmp = itemsOut
            itemsOut = []
            for ind in playerInds:
                itemsOut.append(itemsTmp[ind])
        if suit != None:
            suitsInds = [i.getSuit() for i in itemsOut]
            suitInds = [i for i, x in enumerate(suitsInds) if x == suit]
            itemsTmp = itemsOut
            itemsOut = []
            for ind in suitInds:
                itemsOut.append(itemsTmp[ind])                
        if notPlayedOnly:                
            playedInds = [i.played for i in itemsOut]
            plInds = [i for i, x in enumerate(playedInds) if x == False]
            itemsTmp = itemsOut
            itemsOut = []
            for ind in plInds:
                itemsOut.append(itemsTmp[ind])             
        if self.DEBUG > 5:
            print("Cards List:")
            for item in itemsOut:
                print("Ind=%3d | Name=%4s | Value= %3d | Player=%d | faceDown=%r " % \
                     (item.ind, item.name, item.getValue(), item.player, item.faceDown) )            
            print("Total cards num = " + str(len(itemsOut)))
        return itemsOut
        

    def buildDeckList(self,with_joker=False):
        suits = ['c','d','h','s']
        ranks = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
        l = list()
        for suit in suits:
            for rank in ranks:
                l.append(suit + '_' + rank)
        if with_joker:
            l.append('j_b')
            l.append('j_r')            
        return l

    
    def dealDeck(self):
        d = self.buildDeckList()        
        random.shuffle(d)
        print(d)
        playerNum=1
        n=1
        c2=0
        dx = [0,self.defHandSpacing,0,self.defHandSpacing]
        dy = [self.defHandSpacing,0,self.defHandSpacing,0]        
        x, y, ang = self.playersHandsPos[playerNum-1]
        for card in d:            
            self.addCard(card,player=playerNum)            
            self.getCardsList()[0].setPos(x+dx[playerNum-1]*c2,
                                           y+dy[playerNum-1]*c2)
            self.getCardsList()[0].rotate(ang)
            
            if n % (52 / self.numOfPlayers) == 0:
                playerNum += 1                
                if playerNum > self.numOfPlayers:
                    break
                x, y, ang = self.playersHandsPos[playerNum-1]
                c2=0
            n += 1
            c2 += 1        



def main():
    app = QApplication(sys.argv)
    form = cardTableWidget()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()