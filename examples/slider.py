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

        sld = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        sld.setFocusPolicy(QtCore.Qt.NoFocus)
        sld.setGeometry(30, 40, 100, 30)
        sld.valueChanged[int].connect(self.changeValue)
        
        self.label = QtWidgets.QLabel(self)
        self.label.setPixmap(QtGui.QPixmap('volume_mute.png'))
        self.label.setGeometry(160, 40, 80, 30)
        
        self.setGeometry(300, 300, 280, 170)
        self.setWindowTitle('QtGui.QSlider')
        self.show()
        
    def changeValue(self, value):

        if value == 0:
            self.label.setPixmap(QtGui.QPixmap('volume_mute.png'))
        elif value > 0 and value <= 50:
            self.label.setPixmap(QtGui.QPixmap('volume_down.png'))
        elif value > 50:
            self.label.setPixmap(QtGui.QPixmap('volume_up.png'))

def main():
    
    app = QtWidgets.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()