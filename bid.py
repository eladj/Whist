# -*- coding: utf-8 -*-
from __future__ import print_function
from PyQt4.QtCore import *
from PyQt4.QtGui  import *
import sys
import os


class BiddingDialog(QWidget):
    path = "data" #path where the icons file exist
    
    index2SuitName = {4:'No Trump', 3:'Spades', 2:'Hearts', 1:'Diamonds', 0:'Clubs'}
    index2ImgName = {4:"SuitNT.png", 3:"SuitSpades.svg", 2:"SuitHearts.svg", 1:"SuitDiamonds.svg", 0:"SuitClubs.svg"}
    suit2Index = {'notrump':4, 's':3, 'h':2,'d':1, 'c':0}        
    Name2Char = {'No Trump':'notrump', 'Spades':'s','Hearts':'h', 'Diamonds':'d', 'Clubs':'c'}
    
    finishedBidding = pyqtSignal()
    
    def __init__(self, AI_players, AIlevel, playerToBid):
        super(BiddingDialog, self).__init__()
        #self.trumpSelected = False # first bidding stage
        self.bidsArchive = [[],[],[],[]]
        self.bids2Archive = [[],[],[],[]]        
        self.maxBidValue = -1
        self.maxBidSuit = 0        
        self.AIlevel = AIlevel
        self.playerAI = AI_players
        self.playerToBid = playerToBid                      
        self.finalBids = None
        self.finalTrump = None
        self.initUI()
        self.manageBids()

    def initUI(self):        
        self.pic = QLabel()           
        self.pic.setPixmap(QPixmap("icon.png"))        
        text1 = QLabel()
        text1.setText('First bidding - select trump')
        text1.setAlignment(Qt.AlignCenter)
        text1.setFont(QFont("times",pointSize=16, weight=1))
        self.text1 = text1
        text2 = QLabel()
        text2.setText('Place Your Bid:')        
        text2.setAlignment(Qt.AlignLeft)
        text2.setFont(QFont("times",pointSize=12, weight=-1))
        self.text2 = text2
        bidValue = QSpinBox()
        bidValue.setMinimum(0)
        bidValue.setMaximum(13)
        self.bidValue = bidValue
        bidSuit = QComboBox()
        bidSuit.addItem("Clubs")
        bidSuit.addItem("Diamonds")
        bidSuit.addItem("Hearts")
        bidSuit.addItem("Spades")        
        bidSuit.addItem("No Trump")
        for ind in range(4):
            bidSuit.setItemIcon(ind,QIcon(os.path.join(self.path,self.index2ImgName[ind])))
                
        self.bidSuit = bidSuit
        self.bidsTextList = QListWidget()
        
        self.passButton = QPushButton("Pass")
        self.bidButton = QPushButton("Bid")        
        self.passButton.clicked.connect(self.applyPass)
        self.bidButton.clicked.connect(self.applyBid)

        hbox = QHBoxLayout()
        hbox.addWidget(self.passButton)
        hbox.addStretch(1)
        hbox.addWidget(self.bidButton)
        
        hbox2 = QHBoxLayout()
        hbox2.addWidget(bidValue)
        hbox2.addWidget(bidSuit)

        vbox = QVBoxLayout()
        #vbox.addStretch(1)        
        vbox.addWidget(self.text1)        
        vbox.addStretch(1)
        vbox.addWidget(self.text2)
        vbox.addLayout(hbox2)
        vbox.addStretch(1)
        vbox.addLayout(hbox)
        vbox.addWidget(self.pic)
        vbox.addWidget(self.bidsTextList)
        
        self.setLayout(vbox)    
                   
        #self.setGeometry(300, 300, 300, 150)
        self.center()
        self.setWindowTitle('Bidding')       
        
    def manageBids(self):        
        if self.playerAI[self.playerToBid-1] == []: # if human player
            return
        else: # if it's AI player
           bid, selectedTrump = self.playerAI[self.playerToBid-1].bid()
           if self.checkIfBidLegal1(bid, selectedTrump):
               self.bidValue.setValue(bid)           
               self.bidSuit.setCurrentIndex(self.suit2Index[selectedTrump])
               print("player %d is applying bid" % self.playerToBid)
               self.applyBid()           
           else:
               print("Bid is illegal - player %d: bid=%d suit=%s"
                       % (self.playerToBid,bid,selectedTrump))
               self.applyPass()
    
    
    def manageBids2(self):
        if self.playerAI[self.playerToBid-1] == []: # if human player
            return
        else: # if it's AI player
           selectedSuit = self.Name2Char[self.index2SuitName[self.maxBidSuit]]
           bid, tmp = self.playerAI[self.playerToBid-1].bid(forcedTrump=selectedSuit)
           if self.checkIfBidLegal2(bid):
               self.bidValue.setValue(bid)                          
               print("player %d is applying bid" % self.playerToBid)
               self.applyBid2()
           else:
               print("Bid is illegal - player %d: bid=%d suit=%s"
                       % (self.playerToBid,bid,selectedTrump))
               print("Total bidding sum cannot be exactly 13")
               bid = self.playerAI[self.playerToBid-1].bid(forcedTrump=selectedSuit,notAlowedBid=bid)
               self.bidValue.setValue(bid)                          
               print("player %d is applying bid" % self.playerToBid)
               self.applyBid2()       


    def checkIfBidLegal1(self,bid,trump):
        """ check if bid is legal for the first round of bidding (no trump
        has yet been decided)
        """
        if bid < self.maxBidValue:               
               return False
        if bid == self.maxBidValue: #if value equal, check suits (c<d<h<s<NT)
               if self.suit2Index[trump] <= self.maxBidSuit:                   
                   return False        
        return True

        
    def checkIfBidLegal2(self,bid):
        """ check if bid is legal for the second round of bidding (trump
        has been decided)
        """
        print("checkIfBidLegal2: ",bid,self.bids2Archive)
        print("self.bids2Archive.count([])",self.bids2Archive.count([]))
        if self.bids2Archive.count([]) == 1: # if it is the last player
            totalBids = 0
            for b in self.bids2Archive:
                if b != []:
                    totalBids += b
            print("totalBids+bid", totalBids + bid) 
            if totalBids + bid == 13: # total sum cannot be 13
                return False
        return True
        
        
    def addBidToList(self,player, bid, trump):
        if bid == -100: #pass
            self.bidsTextList.addItem("Player %d: pass" % player)
        else:
            self.bidsTextList.addItem("Player %d: %d %s" % (player,bid,trump))
                

    def applyPass(self):        
        self.bidsArchive[self.playerToBid-1] = -100
        self.addBidToList(self.playerToBid,-100,-100) #pass
        print("Player %d: passed" % self.playerToBid)
        
        if self.bidsArchive.count([]) == 0:  # if all players placed bet
            if sum(self.bidsArchive) < -201: # only if 3 players already pass
                self.finishBidding1() # finish first round of bidding -> select Trump
                return
        while True:
            self.playerToBid += 1
            if self.playerToBid == 5:
                self.playerToBid = 1
            if self.bidsArchive[self.playerToBid-1] != -100:
                break
        print("Next Player to Bid: %d" % self.playerToBid)
        print("applyPass->self.bidsArchive",self.bidsArchive)
        self.manageBids()
        
        
    def applyBid(self):        
        if self.playerAI[self.playerToBid-1] == []: # check user input
            if self.checkIfBidLegal1(self.bidValue.value(),
             self.Name2Char[self.index2SuitName[self.bidSuit.currentIndex()]]) == False:
                item = QListWidgetItem()
                item.setText("You cannot bid less than the maximum bid")
                item.setForeground(Qt.red)
                self.bidsTextList.addItem(item)
                print("You cannot bid less than the maximum bid")                     
                return
        self.addBidToList(self.playerToBid, self.bidValue.value(), 
                          self.index2SuitName[self.bidSuit.currentIndex()])
        self.maxBidValue = self.bidValue.value()
        self.maxBidSuit = self.bidSuit.currentIndex()
        self.bidsArchive[self.playerToBid-1] = self.bidValue.value()        
        while True:
            self.playerToBid += 1
            if self.playerToBid == 5:
                self.playerToBid = 1
            if (self.bidsArchive[self.playerToBid-1] != -100) or \
               (self.bidsArchive[self.playerToBid-1] == []):
                break
        print("Next Player to Bid: %d" % self.playerToBid)
        print("applyBid->self.bidsArchive",self.bidsArchive)
        self.manageBids()
        #self.deleteLater()


    def applyBid2(self):
        if self.playerAI[self.playerToBid-1] == []: # check user input
            if self.checkIfBidLegal2(self.bidValue.value()) == False:
                item = QListWidgetItem()
                item.setText("Sum of bids cannot be exactly 13")            
                item.setForeground(Qt.red)
                self.bidsTextList.addItem(item)
                print("Sum of bids cannot be 13")                     
                return                                 
        self.bids2Archive[self.playerToBid-1] = self.bidValue.value()
        self.addBidToList(self.playerToBid, self.bidValue.value(), 
                          self.index2SuitName[self.bidSuit.currentIndex()])
        print("applyBid2: ",self.bids2Archive)                     
        if self.bids2Archive.count([]) == 0:
            self.finishBidding2()
            return
        else:
            self.playerToBid += 1
            if self.playerToBid == 5:
                self.playerToBid = 1
        print("applyBid2: next player to bid: player %d" % self.playerToBid)                     
        self.manageBids2()
 
           
    def finishBidding1(self):        
        ind = self.bidsArchive.index(max(self.bidsArchive))
        self.playerToBid = ind+1 # first to bid is the player who selected the trump
        item = QListWidgetItem()
        item.setText("First bidding round finished")
        item.setForeground(Qt.green)
        item2 = QListWidgetItem()
        item2.setText("Player %d selected trump: %s" %
                      (self.playerToBid,self.index2SuitName[self.maxBidSuit]))
        item2.setForeground(Qt.green)        
        self.bidsTextList.addItem(item)
        self.bidsTextList.addItem(item2)
        self.text1.setText('Second bidding - %s' % 
            self.index2SuitName[self.maxBidSuit])
        self.pic.setPixmap(QPixmap(os.path.join(self.path,self.index2ImgName[self.maxBidSuit])))
        self.bidSuit.setCurrentIndex(self.maxBidSuit)
        self.bidSuit.setEnabled(False)
        self.passButton.deleteLater()
        self.bidButton.clicked.disconnect(self.applyBid)
        self.bidButton.clicked.connect(self.applyBid2)
        #self.update()        
        self.manageBids2()
        
        
    def finishBidding2(self):
        item = QListWidgetItem()
        item.setText("Bidding finished")            
        item.setForeground(Qt.green)
        self.bidsTextList.addItem(item)
        self.bidButton.setText("Close")
        self.bidButton.clicked.disconnect(self.applyBid2)
        self.bidButton.clicked.connect(self.close)
        #TODO - something that will pass this value
        self.finalBids = self.bids2Archive
        self.finalTrump = self.Name2Char[self.index2SuitName[self.maxBidSuit]]
        
        
    def close(self):
        """ close bidding window and emit signal to manageGame to start the game """
        self.finishedBidding.emit()
        self.deleteLater()
        
    def center(self):       
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = BiddingDialog()
    #widget.setGeometry(QRect(50,50,1024,576))
    widget.setWindowIcon(QIcon('icon.png'))
    widget.show()
    sys.exit(app.exec_())    