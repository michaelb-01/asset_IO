from PySide2 import QtCore, QtGui, QtWidgets

import variables

primary = QtGui.QColor(207,66,53)

class iconButton(QtWidgets.QWidget):
	clicked = QtCore.Signal()

	def __init__(self, colour='white', hoverColour=None):
		super(iconButton, self).__init__()

		self.colour = colour

		if hoverColour:
			self.hoverColour = hoverColour
		else:
			self.hoverColour = primary
		
		self.initUI()		

	def initUI(self):    
		# create main layout and set margin to 0
		mainLayout = QtWidgets.QVBoxLayout()
		mainLayout.setContentsMargins(0, 0, 0, 0)

		# icon image
		self.pixmap = QtGui.QPixmap('plus.png')
		# get alpha from pixmap
		self.mask = self.pixmap.createMaskFromColor( QtCore.Qt.transparent )
		self.pixmap.fill(self.colour)
		# apply alpha
		self.pixmap.setMask(self.mask)

		# create button (label) and apply pixmap as the image
		self.button = QtWidgets.QLabel()
		self.button.setPixmap(self.pixmap)

		#self.c.closeApp.emit()

		# add button to layout
		mainLayout.addWidget(self.button)

		# set layout
		self.setLayout(mainLayout)

	def enterEvent(self, event):
		# fill pixmap, you then have to reset the mask and reapply it to the button...
		self.pixmap.fill(self.hoverColour)
		self.pixmap.setMask(self.mask)
		self.button.setPixmap(self.pixmap)

	def leaveEvent(self, event):
		# fill pixmap, you then have to reset the mask and reapply it to the button...
		self.pixmap.fill(self.colour)
		self.pixmap.setMask(self.mask)
		self.button.setPixmap(self.pixmap)

	def mousePressEvent(self, event):
		self.clicked.emit()
