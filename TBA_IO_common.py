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

class TBA_AssetList(QtWidgets.QWidget):
	
	def __init__(self):
		super(TBA_AssetList, self).__init__()
		
		self.initUI()

	def initUI(self):    
		self.assetList = TBA_list()

class exporter(QtWidgets.QWidget):

	def __init__(self):
		super(exporter, self).__init__()

		# are we importer or exporter?
		self.importer = True

		# directory paths
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
		if not item:
			return

		self.selAsset = item.text()
		self.updateTypeList()

	def onTypeSelected(self, item):
		if not item:
			return

		print 'type selected'
		self.selType = item.text()
		self.updateVersionList()

	def onVersionSelected(self, item):
		if not self.versionList.footer:
			return

		if item:
			self.versionList.footer.setText('Write Version: ' + item.text())
		else:
			self.versionList.footer.setText('Write Version: ')
		print 'version selected'

	def updateTypeList(self):
		# if this is the importer UI we need to filter by exported types

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
		 
		 	# if we are in the importer set the selectability of the item
		 	# else just change the colour to illustrate what has already been exported
			if item.text() in types:
				self.enableItem(item)
			else:
				if self.importer:
					self.disableItem(item)
				else:
					self.darkenItem(item)
				

		# update types header
		self.typeList.updateNumItems()

		# update the version list
		self.updateVersionList()

	def disableAllTypes(self):
		# disable all type items
		if self.importer:
			for i in range(self.typeList.tbaList.count()):
				self.disableItem(self.typeList.tbaList.item(i))
		else:
			for i in range(self.typeList.tbaList.count()):
				self.darkenItem(self.typeList.tbaList.item(i))

		# update the version list
		self.updateVersionList()

	def enableItem(self, item):
		item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
		item.setTextColor(QtGui.QColor('white'))

	def disableItem(self, item):
		item.setFlags(QtCore.Qt.NoItemFlags)

	def darkenItem(self, item):
		item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
		item.setTextColor(QtGui.QColor(50,50,50))

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

		# update versions header
		self.versionList.updateNumItems()

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
		self.packageList = TBA_UI.TBA_list()
		self.packageList.setHeader('Packages')
		
		# asset list
		self.assetList = TBA_UI.TBA_list()
		self.assetList.setHeader('Assets')
		self.assetList.tbaList.currentItemChanged.connect(self.onAssetSelected)

		self.assetList.addCreateButton()
		self.assetList.createButton.clicked.connect(self.addAssetDialog)

		# type list
		self.typeList = TBA_UI.TBA_list()
		self.typeList.setHeader('Types')
		self.typeList.tbaList.currentItemChanged.connect(self.onTypeSelected)

		# version list
		self.versionList = TBA_UI.TBA_list()
		self.versionList.setHeader('Versions')
		self.versionList.setFooter('Write Version: ')
		self.versionList.tbaList.currentItemChanged.connect(self.onVersionSelected)
		
		self.versionModeToggle = TBA_UI.radioButton()
		self.versionList.headerLayout.addWidget(self.versionModeToggle)

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