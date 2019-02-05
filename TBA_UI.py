from PySide2 import QtCore, QtGui, QtWidgets

import variables

primary = QtGui.QColor(207,66,53)

class iconButton(QtWidgets.QWidget):
    clicked = QtCore.Signal()

    def __init__(self, colour='#ccc', hoverColour=None):
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

class radioButton(QtWidgets.QWidget):
    clicked = QtCore.Signal()

    def __init__(self, colour='white', hoverColour=None):
        super(radioButton, self).__init__()

        self.colour = colour

        if hoverColour:
            self.hoverColour = hoverColour
        else:
            self.hoverColour = primary

        self.initUI()

    def initUI(self):
        # create main layout and set margin to 0
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setContentsMargins(20, 20, 20, 20)

        self.setStyleSheet('background-color:red')

        # add button to layout
        #mainLayout.addWidget(self.button)

        # set layout
        self.setLayout(mainLayout)

    def paintEvent(self, e):

        paint = QtGui.QPainter()
        #

        paint.begin(self)
        self.drawInner(paint)
        self.drawOuter(paint)
        paint.end()

    def drawInner(self, paint):
        color = QtGui.QColor(0, 0, 0)
        color.setNamedColor('#40A299')

        paint.setRenderHint(QtGui.QPainter.Antialiasing)
        paint.setPen(color)
        paint.setBrush(color)

        width = 10

        paint.drawEllipse(9.5, 9.5, width, width)

    def drawOuter(self, paint):
        color = QtGui.QColor(0, 0, 0)
        color.setNamedColor('#40A299')

        paint.setRenderHint(QtGui.QPainter.Antialiasing)
        paint.setPen(QtGui.QPen(color,3) )
        paint.setBrush(QtGui.QColor(0, 0, 0, 0))

        width = 24

        paint.drawEllipse(3, 3, width, width)

class TBA_list_draggable(QtWidgets.QListWidget):
    rightClicked = QtCore.Signal(list)
    selItem = None

    def __init__(self):
        super(TBA_list_draggable, self).__init__()

        # for drag and drop
        self.selItem = None

        self.itemPressed.connect(self.item_click)

    def item_click(self, item):
        self.selItem = item

    def contextMenuEvent(self, event):
        if not self.selectedItems():
            print('No item selected')
            return

        # send selected text and position relative to current widget
        item = self.selectedItems()[0]

        self.rightClicked.emit([item, self.mapToGlobal(event.pos())])

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            super(TBA_list_draggable, self).dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            super(TBA_list_draggable, self).dragMoveEvent(event)

    def dropEvent(self, event):
        print('TBA :: dropEvent')

        droppedItem = event.source().selItem

        if droppedItem:
            print('Dropped items text: {0}'.format(droppedItem.text()))
            if self.findItems(droppedItem.text(), QtCore.Qt.MatchExactly):
                print('Ignoring duplicate')
                event.ignore()
                return

        if event.mimeData().hasUrls():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            links = []
            for url in event.mimeData().urls():
                links.append(str(url.toLocalFile()))
            self.emit(QtCore.SIGNAL("dropped"), links)
        else:
            event.setDropAction(QtCore.Qt.MoveAction)
            super(TBA_list_draggable, self).dropEvent(event)

    def select_first_enabled(self):
        for i in range(self.count()):
            if self.item(i).flags() & QtCore.Qt.ItemIsSelectable:
                self.setCurrentRow(i)
                self.setFocus()

class TBA_list(QtWidgets.QWidget):
    rightClicked = QtCore.Signal(QtCore.QEvent)

    def __init__(self):
        super(TBA_list, self).__init__()

        self.setObjectName("tbaList")

        self.numItems = 0
        self.headerText = ''

        # set empty variable for header
        self.header = None
        self.footer = None
        self.footerPrefix = None

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        # create list widget
        self.tbaList = QtWidgets.QListWidget()
        #self.tbaList.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.tbaList.setDragDropMode(self.tbaList.InternalMove)

    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        margin = 0
        main_layout.setContentsMargins(margin, margin, margin, margin)
        main_layout.setSpacing(0)

        # create header, content and footer layouts
        # header
        self.headerLayout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(self.headerLayout)
        # content
        self.contentLayout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(self.contentLayout)
        # footer
        self.footerLayout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(self.footerLayout)

        # add list to content layout
        self.contentLayout.addWidget(self.tbaList)

    def create_connections(self):
        # update header when an item changes or items are inserted or removed
        #self.tbaList.currentItemChanged.connect(self.onItemChanged)
        self.tbaList.model().rowsInserted.connect(self.itemAdded)
        self.tbaList.model().rowsRemoved.connect(self.itemAdded)

    def setHeader(self, text, showNum=True):
        # create header if it doesn't exist
        if not self.header:
            self.header = QtWidgets.QLabel(objectName='header')

        self.header.setText(text)
        # insert the header at 0 index with stretch factor of 1
        self.headerLayout.insertWidget(0,self.header,1)

        self.headerText = text

        if showNum:
            self.updateNumItems()

    def setFooter(self, text):
        print('set footer text')
        if not self.footer:
            self.footer = QtWidgets.QLabel(objectName='footer')
            self.footerPrefix = QtWidgets.QLabel('Write: ')

            self.footerLayout.insertWidget(0,self.footer,0)
            self.footerLayout.insertWidget(0,self.footerPrefix,0)

        self.footer.setText(text)

    def addCreateButton(self):
        self.createButton = iconButton()

        self.headerLayout.addWidget(self.createButton)

    def updateNumItems(self):
        # add number of selectable items in brackets to the header
        num = 0

        for i in range(self.tbaList.count()):
            if self.tbaList.item(i).flags() & QtCore.Qt.ItemIsSelectable:
                num += 1

        if self.header:
            self.header.setText(self.headerText + ' (' + str(num) + ')')

    def itemAdded(self, itemIndex):
        # scroll to the last item
        num = self.tbaList.count()

        self.tbaList.scrollToItem(self.tbaList.item(num-1))
        self.updateNumItems()

    def contextMenuEvent(self, event):
        print('contextMenuEvent')
        print(event)

        if not self.tbaList.selectedItems():
            print('No item selected')
            return

        self.rightClicked.emit(self.mapToGlobal(event.pos()))

