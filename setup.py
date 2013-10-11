# -*- coding: utf-8 -*-
#from distutils.core import setup
#import py2exe
#setup(console=['main.py'])

""" for PyQt App """
#from py2exe.build_exe import py2exe
#from distutils.core import setup
#setup( console=[{"script": "main.py"}] )

#This also works:
from distutils.core import setup
import py2exe
setup(windows=[{"script":"main.py"}], 
               options={"py2exe":{"includes":
                   ["sip","PyQt4.QtCore","PyQt4.QtGui"]}})