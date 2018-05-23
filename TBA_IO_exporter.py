import sys

from PySide2 import QtCore, QtGui, QtWidgets
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
import maya.cmds as mc

import TBA_IO_common
reload(TBA_IO_common)

class TBA_IO_exporter(QtWidgets.QWidget):

	def __init__(self):
		super(TBA_IO_exporter, self).__init__()
		
		self.initUI()
		self.mayaAttachWindow()

	def mayaAttachWindow(self):
		# this fuction attaches the ui to a maya main window so that is shows up inside maya
		# declare an object name for the window
		self.windowObjectName = 'TBA_Asset_Manager'

		# check if any other instances of the window exists -- if so close them
		if mc.window(self.windowObjectName, exists = 1):
			mc.deleteUI(self.windowObjectName, window = 1)

		# get the maya main window from the maya api
		windowPointer = omui.MQtUtil.mainWindow()
		mayaMainWindow = wrapInstance(long(windowPointer), QtWidgets.QWidget)

		# create a parent window that is connected to the maya main window
		self.parentWindow = QtWidgets.QMainWindow(mayaMainWindow)
		self.parentWindow.setObjectName(self.windowObjectName)
		self.parentWindow.setAttribute(QtCore.Qt.WA_DeleteOnClose)
		self.parentWindow.setWindowTitle('TBA Asset Manager')

		# add the asset publisher UI to the parent window
		self.parentWindow.setCentralWidget(self)

		# set the size of the window
		self.parentWindow.setGeometry(300,300,150,150)

	def initUI(self):      		
		self.setGeometry(300, 300, 290, 150)
		self.setWindowTitle('Input dialog')

		commonUI = TBA_IO_common.TBA_IO_UI()

		mainLayout = QtWidgets.QVBoxLayout(self)

		mainLayout.addWidget(commonUI.assetList)

		self.setLayout(mainLayout)

def main():
	ui = TBA_IO_exporter()

	ui.parentWindow.show()