import sys
import os

from PySide2 import QtCore, QtGui, QtWidgets

import TBA_UI

import sqss_compiler

import re

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

		# set empty variable for header
		self.header = None

	def setHeader(self, text):
		# create header if it doesn't exist
		if not self.header:
			self.header = QtWidgets.QLabel(objectName='header')

		self.header.setText(text)
		# insert the header at 0 index with stretch factor of 1
		self.headerLayout.insertWidget(0,self.header,1)

	def oldHeader(self, text):
		header = QtWidgets.QLabel(objectName='header')
		header.setText(text)

		# insert the header at 0 index with stretch factor of 1
		self.headerLayout.insertWidget(0,header,1)

	def addCreateButton(self):
		self.createButton = TBA_UI.iconButton()

		self.headerLayout.addWidget(self.createButton)

class TBA_AssetList(QtWidgets.QWidget):
	
	def __init__(self):
		super(TBA_AssetList, self).__init__()
		
		self.initUI()

	def initUI(self):    
		self.assetList = TBA_list()

class exporter(QtWidgets.QWidget):

	def __init__(self):
		super(exporter, self).__init__()

		self.publishDir = None
		self.assetsDir = None

		# selected items
		self.selPackage = None
		self.selAsset = None
		self.selType = None
		self.selVersion = None

		print 'init exporter'

		self.getPublishDir()

		if not self.publishDir or not self.assetsDir:
			print 'could not find correct _published3d/assets folder, exiting'
			QtCore.QCoreApplication.quit
			return
		
		self.initUI()
		self.initPackageList()
		self.initAssetList()
		self.initTypeList()

	def getPublishDir(self):
		# this function would look up the _published3d directory relative to the scene
		currentDir = os.path.dirname(os.path.realpath(__file__))
		publishDir = os.path.join(currentDir, '_published3d')

		self.publishDir = publishDir
		self.assetsDir = os.path.join(self.publishDir, 'assets')

	def initPackageList(self):
		packageDir = os.path.join(self.publishDir, 'packages')

		# exit if packages directory can't be found
		if not os.path.isdir(packageDir):
			return

		# get packages from dir
		packages = sorted(os.listdir(packageDir))

		# add packages to package list
		for package in packages:
			self.packageList.tbaList.addItem(package)

	def initAssetList(self):
		print 'init assets'
		#self.assetList.tbaList.addItem('test')

		# get assets from dir
		assets = sorted(os.listdir(self.assetsDir))

		# add assets to asset list
		for asset in assets:
			self.assetList.tbaList.addItem(asset)

	def initTypeList(self):
		types = ['camera', 'model', 'anim', 'fx', 'rig', 'light', 'shaders']
		for item in types:
			self.typeList.tbaList.addItem(item)

		self.updateTypeList()

	def onAssetSelected(self, item):
		self.selAsset = item.text()
		self.updateTypeList()

	def onTypeSelected(self, item):
		print 'type selected'
		self.selType = item.text()
		self.updateVersionList()

	def updateTypeList(self):
		# if no asset is selected disable types and return
		if not self.selAsset:
			self.disableAllTypes()
			return

		# asset directory
		assetDir = os.path.join(self.assetsDir, self.selAsset)

		# if asset path does not exist
		if not os.path.isdir(assetDir):
			self.disableAllTypes()
			return
		
		# list folders inside assetDir
		types = sorted(os.listdir(assetDir))

		# iterate over types and disable if not found
		for i in range(self.typeList.tbaList.count()):
			item = self.typeList.tbaList.item(i)
		 
			if item.text() in types:
				# enable item and make it selectable
				item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
			else:
				item.setFlags(QtCore.Qt.NoItemFlags)

		# update the version list
		self.updateVersionList()

	def disableAllTypes(self):
		# disable all type items
		for i in range(self.typeList.tbaList.count()):
			self.typeList.tbaList.item(i).setFlags(QtCore.Qt.NoItemFlags)

		# update the version list
		self.updateVersionList()

	def updateVersionList(self):
		# clear all items, will repopulate later in this function
		self.versionList.tbaList.clear()

		# if no type is selected remove all versions from the list and return
		if not self.selType:
			return

		# type directory
		typeDir = os.path.join(self.assetsDir, self.selAsset, self.selType)

		# if type directory does not exist clear and return
		if not os.path.isdir(typeDir):
			return

		# list version folders inside typeDir
		versions = sorted(os.listdir(typeDir))

		# iterate over folders and add to version list if named correctly
		for version in versions:
			# folder must match format of 'v' then three digits, e.g. v007
			if re.match("v[0-9]{3}", version):
				self.versionList.tbaList.addItem(version)

	def addAssetDialog(self):
		name, ok = QtWidgets.QInputDialog.getText(self, 'Input Dialog', 
			'Enter your name:')
		
		if ok:
			#self.le.setText(str(text))
			if len(self.assetList.tbaList.findItems(name, QtCore.Qt.MatchRegExp)) == 0:
				self.assetList.tbaList.addItem(name)

	# handles key events for navigating left and right between lists
	def keyPressEvent(self, event):
		print 'key pressed'
		key = event.key()

		if key == QtCore.Qt.Key_Right:
			# if 'active' list is selType select last version
			if self.selType:
				num = self.versionList.tbaList.count()
				if num == 0:
					return
				item = self.versionList.tbaList.item(num-1)
				self.versionList.tbaList.setCurrentItem(item)
				self.selVersion = item.text()
				self.versionList.tbaList.setFocus()
			elif self.selAsset:
				# select first selectable item
				for i in range(self.typeList.tbaList.count()):
					if self.typeList.tbaList.item(i).flags() & QtCore.Qt.ItemIsSelectable:
						self.typeList.tbaList.setCurrentRow(i)
						self.typeList.tbaList.setFocus()
						return
			else:
				# select first selectable item
				for i in range(self.assetList.tbaList.count()):
					if self.assetList.tbaList.item(i).flags() & QtCore.Qt.ItemIsSelectable:
						self.assetList.tbaList.setCurrentRow(i)
						self.assetList.tbaList.setFocus()
						return
		elif key == QtCore.Qt.Key_Left:
			if self.selVersion:
				self.typeList.tbaList.setFocus()
				self.selVersion = None
				self.updateVersionList()
			elif self.selType:
				self.assetList.tbaList.setFocus()
				self.selType = None
				# deselect all
				self.typeList.tbaList.setCurrentRow(-1)
				self.updateTypeList()

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
		self.packageList = TBA_list()
		self.packageList.setHeader('Packages')
		
		# asset list
		self.assetList = TBA_list()
		self.assetList.setHeader('Assets')
		self.assetList.tbaList.currentItemChanged.connect(self.onAssetSelected)

		self.assetList.addCreateButton()
		self.assetList.createButton.clicked.connect(self.addAssetDialog)

		# type list
		self.typeList = TBA_list()
		self.typeList.setHeader('Types')
		self.typeList.tbaList.currentItemChanged.connect(self.onTypeSelected)

		# type list
		self.versionList = TBA_list()
		self.versionList.setHeader('Versions')

		# add lists to listsLayout
		listsLayout.addWidget(self.packageList)
		listsLayout.addWidget(self.assetList)
		listsLayout.addWidget(self.typeList)
		listsLayout.addWidget(self.versionList)

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