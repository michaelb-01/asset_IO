#!/usr/bin/python
# -*- coding: utf-8 -*-

# simple.py

import sys
from PySide2 import QtGui
from PySide2.QtWidgets import QApplication, QLabel, QWidget

app = QApplication(sys.argv)

wid = QWidget()
wid.resize(250, 150)
wid.setWindowTitle('Simple')
wid.show()

app.exec_()