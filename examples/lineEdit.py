#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ZetCode PySide tutorial 

In this example, we select a colour value
from the QtGui.QColorDialog and change the background
colour of a QtGui.QFrame widget. 

author: Jan Bodnar
website: zetcode.com 
last edited: August 2011
"""

import sys
from PySide2 import QtGui, QtWidgets, QtCore

class Example(QtWidgets.QWidget):
    
    def __init__(self):
        super(Example, self).__init__()
        
        self.initUI()
        
    def initUI(self):      

        self.lbl = QtWidgets.QLabel(self)
        qle = QtWidgets.QLineEdit(self)
        
        qle.move(60, 100)
        self.lbl.move(60, 40)

        qle.textChanged[str].connect(self.onChanged)
        
        self.setGeometry(300, 300, 280, 170)
        self.setWindowTitle('QtWidgets.QLineEdit')
        self.show()
        
    def onChanged(self, text):
        
        self.lbl.setText(text)
        self.lbl.adjustSize()       
        
def main():
    
    app = QtWidgets.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()