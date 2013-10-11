# -*- coding: utf-8 -*-
from __future__ import print_function
from PyQt4.QtCore import *
from PyQt4.QtGui  import *
import sys
import os
from cardswhist import CardTableWidgetWhist

path = 'data'        

class MainWindow(QMainWindow):
        
    
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        # create widgets
        self.cardsTable = CardTableWidgetWhist()        
        menubar = self.menuBar()
        mainMenu = menubar.addMenu('&Main')
        helpMenu = menubar.addMenu('&Help')        
        newGameAction = QAction('&New Game', self)
        newGameAction.setShortcut('Ctrl+N')
        newGameAction.setStatusTip('Start New Game')        
        helpRulesAction = QAction('&Rules', self)
        helpRulesAction.setStatusTip('Show the rules of the game')
        helpRulesAction.triggered.connect(self.openRulesPopup)
        helpAboutAction = QAction('&About', self)
        helpAboutAction.triggered.connect(self.openAboutPopup)        
        mainMenu.addAction(newGameAction)
        helpMenu.addAction(helpRulesAction)
        helpMenu.addAction(helpAboutAction)

        
        # main layout
        self.mainLayout = QVBoxLayout()        
        # add all widgets to the main vLayout        
        self.mainLayout.addWidget(self.cardsTable) 
        # central widget
        self.centralWidget = QWidget()
        self.centralWidget.setLayout(self.mainLayout)                
        # set central widget
        self.setCentralWidget(self.centralWidget)
            
    def openRulesPopup(self):        
         self.wRules = rulesPopup()
         self.wRules.show()
        
    def openAboutPopup(self):        
        self.wAbout = AboutPopUP()
        self.wAbout.show()   
        
class AboutPopUP(QWidget):
            
    def __init__(self):
        super(AboutPopUP, self).__init__()
        self.initUI()
        
    def initUI(self):
        pic = QLabel()           
        pic.setPixmap(QPixmap(os.path.join(path,'icon.png')))
        text1 = QLabel()
        text1.setText(QString('PyWhist 0.1.2'))
        text1.setAlignment(Qt.AlignCenter)
        text1.setFont(QFont("times",pointSize=16, weight=1))
        text2 = QLabel()
        text2.setText(QString(u'Copyright © 2013, Elad Joseph'))        
        text2.setAlignment(Qt.AlignCenter)        
        text3 = QTextEdit()
        with open ("LICENSE.txt", "r") as myfile:
            licenseText = myfile.read().replace('\n', '')        
        text3.setText(licenseText)
        text3.setAlignment(Qt.AlignLeft) 
              
        closeButton = QPushButton("Close")
        #closeButton.clicked.connect(QCoreApplication.instance().quit)
        closeButton.clicked.connect(self.deleteLater)

        hbox = QHBoxLayout()        
        hbox.addStretch(1)
        hbox.addWidget(closeButton)

        vbox = QVBoxLayout()
        #vbox.addStretch(1)
        vbox.addWidget(pic)
        vbox.addWidget(text1)        
        vbox.addWidget(text2)
        vbox.addStretch(1)
        vbox.addWidget(text3)
        vbox.addLayout(hbox)
        
        self.setLayout(vbox)            
        #self.setGeometry(300, 300, 300, 150)
        self.center()
        self.setWindowTitle('About PyWhist')    
    
    def center(self):       
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class rulesPopup(QGraphicsView):
    def __init__(self):
        super(rulesPopup,self).__init__()
        self.scene = QGraphicsScene()        
        self.text = QGraphicsTextItem()
        stream = QFile(os.path.join(path,'rules.html'))
        if stream.open(QFile.ReadOnly):
            self.text.setHtml(QString.fromUtf8(stream.readAll()))
            stream.close()
        self.text.setTextWidth(500)
        self.scene.addItem(self.text)
        self.setGeometry(200,200,550,500)
        self.setScene(self.scene)
        
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.setWindowTitle("Israeli Whist")
    widget.setWindowIcon(QIcon('icon.png'))
    widget.setGeometry(QRect(50,50,1024,576))
    widget.show()
    sys.exit(app.exec_())
    