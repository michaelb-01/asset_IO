import sys
import os

from PySide2 import QtCore, QtGui, QtWidgets

import sqss_compiler

# inherits from QWidget
class TBA_IO_UI(QtWidgets.QWidget):
	
	def __init__(self):
		super(TBA_IO_UI, self).__init__()
		
		self.initUI()
		
	def initUI(self):      

		self.assetList = TBA_assetList()
		self.assetList.clicked.connect(lambda: versionList.test())
		
		versionList = TBA_versionList()

		# mainLayout = QtWidgets.QVBoxLayout(self)

		# mainLayout.addWidget(self.assetList)
		# mainLayout.addWidget(versionList)

	def mousePressEvent(self, event):
		
		self.c.closeApp.emit()

	def showDialog(self):
		text, ok = QtWidgets.QInputDialog.getText(self, 'Input Dialog', 
			'Enter your name:')
		
		if ok:
			self.le.setText(str(text))

class test(QtWidgets.QPushButton):
	
	def __init__(self):
		super(TBA_assetList, self).__init__()
		
		self.initUI()
		
	def initUI(self):      
		self.setText('Test')

		self.clicked.connect(lambda: self.trigger('red'))

	def trigger(self, colour):
		print 'trigger'
		#self.setStyleSheet('background-color:' + colour)

class TBA_list(QtWidgets.QWidget):
	
	def __init__(self):
		super(TBA_list, self).__init__()
		
		self.initUI()

	def initUI(self):    
		self.setObjectName("tbaList")

		# create a layout
		self.mainLayout = QtWidgets.QVBoxLayout()
		margin = 0
		self.mainLayout.setContentsMargins(margin, margin, margin, margin)
		self.mainLayout.setSpacing(0)

		# create header, content and footer layouts
		# header
		self.headerLayout = QtWidgets.QHBoxLayout()
		self.mainLayout.addLayout(self.headerLayout)
		# content
		self.contentLayout = QtWidgets.QHBoxLayout()
		self.mainLayout.addLayout(self.contentLayout)
		# footer
		self.footerLayout = QtWidgets.QHBoxLayout()
		self.mainLayout.addLayout(self.footerLayout)

		# create list widget
		self.tbaList = QtWidgets.QListWidget(self)

		# add list to content layout
		self.contentLayout.addWidget(self.tbaList)

		# set layout
		self.setLayout(self.mainLayout)

	def header(self, text):
		header = QtWidgets.QLabel(objectName='header')
		header.setText(text)
		self.headerLayout.insertWidget(0,header)

	def addCreateButton(self):
		path = QtGui.QPainterPath()
		path.moveTo(20, 80)
		path.lineTo(20, 30)
		
		return
		createButton = QtWidgets.QPushButton()
		createButton.setFixedWidth(32)
		createButton.setFixedHeight(32)
		createButton.setFlat(1)
		createButton.setObjectName('create')
		self.headerLayout.addWidget(createButton)

class TBA_AssetList(QtWidgets.QWidget):
	
	def __init__(self):
		super(TBA_AssetList, self).__init__()
		
		self.initUI()

	def initUI(self):    
		self.assetList = TBA_list()

class exporter(QtWidgets.QWidget):

	def __init__(self):
		super(exporter, self).__init__()

		self.publishDir = 'heellellre'
		print 'init exporter'
		
		self.initUI()
		self.getPublishDir()
		self.initPackages()
		self.initAssets()

	def getPublishDir(self):
		# this function would look up the _published3d directory relative to the scene
		currentDir = os.path.dirname(os.path.realpath(__file__))
		self.publishDir = os.path.join(currentDir, '_published3d')

	def initPackages(self):
		print 'init packges'
		print self.publishDir

	def initAssets(self):
		print 'init assets'
		self.assetList.tbaList.addItem('test')

	def initUI(self):      		
		self.setObjectName("tbaDark")

		# create window on inherited widget
		self.setWindowTitle('TBA Exporter')

		self.resize(800, 300)
		self.centerWindow()

		# main layout to hold all UI
		mainLayout = QtWidgets.QVBoxLayout()
		margin = 10
		mainLayout.setContentsMargins(margin, margin, margin, margin)
		# lists layout for packages, assets, types, versions
		listsLayout = QtWidgets.QHBoxLayout()
		listsLayout.setContentsMargins(0,0,0,0)
		listsLayout.setSpacing(margin)

		# create asset list
		# assetList = TBA_assetList()
		# assetList2 = TBA_assetList()

		# package list
		packageList = TBA_list()
		packageList.header('Packages')
		packageList.tbaList.addItem('jellyMan')
		
		# asset list
		self.assetList = TBA_list()
		self.assetList.header('Assets')

		self.assetList.addCreateButton()

		#self.assetList = TBA_list()

		# for item in ['shoes', 'legs', 'clothes']:
		# 	assetList.tbaList.addItem(item)

		# type list
		typeList = TBA_list()
		typeList.header('Types')
		for item in ['camera', 'model', 'anim', 'fx', 'rig', 'light', 'shader']:
			typeList.tbaList.addItem(item)

		# type list
		versionList = TBA_list()
		versionList.header('Versions')
		for item in ['v001', 'v002', 'v003', 'v004', 'v005']:
			versionList.tbaList.addItem(item)

		# add lists to listsLayout
		listsLayout.addWidget(packageList)
		listsLayout.addWidget(self.assetList)
		listsLayout.addWidget(typeList)
		listsLayout.addWidget(versionList)

		# add listsLayout to mainLayout
		mainLayout.addLayout(listsLayout)

		# set mainLayout as the main layout
		self.setLayout(mainLayout)

		# show the widget (window)
		self.show()

	def centerWindow(self):
		qr = self.frameGeometry()
		cp = QtWidgets.QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft()) 

def main():
	app = QtWidgets.QApplication(sys.argv)
	# set stylesheet

	# compile style sheet
	# arguments are a stylesheet file (using scss for syntax highlighting in sublime), second argument is the variables file
	app.setStyleSheet(sqss_compiler.compile('TBA_stylesheet.scss', 'variables.scss'))

	# with open(stylesheet,"r") as fh:
	#     app.setStyleSheet(fh.read())

	tba = exporter()

	sys.exit(app.exec_())

if __name__ == '__main__':
	main()