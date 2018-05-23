import sys

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

		# create list widget
		self.tbaList = QtWidgets.QListWidget(self)

		# add list to layout
		self.mainLayout.addWidget(self.tbaList)

		# set layout
		self.setLayout(self.mainLayout)

	def header(self, text):
		header = QtWidgets.QLabel(objectName='header')
		header.setText(text)
		self.mainLayout.insertWidget(0,header)

class TBA_assetList(QtWidgets.QWidget):
	
	def __init__(self):
		super(TBA_assetList, self).__init__()
		
		self.initUI()
		
	def initUI(self):    
		self.setObjectName("assetList")

		# create a layout
		mainLayout = QtWidgets.QVBoxLayout()
		margin = 0
		mainLayout.setContentsMargins(margin, margin, margin, margin)
		mainLayout.setSpacing(0)

		# header
		header = QtWidgets.QLabel(objectName='header')
		header.setText("Assets")
		header.setMargin(0)
		# add header to layout
		mainLayout.addWidget(header)

		# create list widget
		assetList = QtWidgets.QListWidget(self)

		assetList.addItem('camera')
		assetList.addItem('shoe')
		assetList.addItem('legs')
		assetList.addItem('clothing')

		# add list to layout
		mainLayout.addWidget(assetList)

		# set layout
		self.setLayout(mainLayout)
		
class exporter(QtWidgets.QWidget):

	def __init__(self):
		super(exporter, self).__init__()
		print 'init exporter'
		

		self.initUI()

	def initUI(self):      		
		
		# create window on inherited widget
		self.setWindowTitle('TBA Exporter')

		self.resize(800, 600)
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

		packageList = TBA_list()
		packageList.tbaList.addItem('test')
		packageList.header('Assets')

		# add assetList to listsLayout
		listsLayout.addWidget(packageList)
		#listsLayout.addWidget(assetList2)

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