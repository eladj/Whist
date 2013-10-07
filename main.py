# -*- coding: utf-8 -*-
from __future__ import print_function
from PyQt4.QtCore import *
from PyQt4.QtGui  import *
from PyQt4.QtWebKit import QWebView
import sys
from cardswhist import CardTableWidgetWhist

class rulesPopup(QWebView):
   def __init__(self):
        QWebView.__init__(self)
        self.loadFinished.connect(self._result_available)

   def _result_available(self, ok):
        frame = self.page().mainFrame()
        print(unicode(frame.toHtml()).encode('utf-8'))
        
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
        newGameAction.triggered.connect(self.cardsTable.newGame)
        helpRulesAction = QAction('&Rules', self)
        helpRulesAction.setStatusTip('Show the rules of the game')
        helpRulesAction.triggered.connect(self.openRulesPopup)
        mainMenu.addAction(newGameAction)
        helpMenu.addAction(helpRulesAction)        

        
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
        self.w = rulesPopup()
        self.w.load(QUrl('http://en.wikipedia.org/wiki/Israeli_whist'))
        #self.w.setGeometry(QRect(100, 100, 400, 200))
        self.w.show()    
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.setWindowTitle("Israeli Whist")
    widget.setWindowIcon(QIcon('icon.png'))
    widget.setGeometry(QRect(50,50,1024,576))
    widget.show()
    sys.exit(app.exec_())