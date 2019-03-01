import sys

from PySide2 import QtCore, QtWidgets

class Chip(QtWidgets.QPushButton):
    def __init__(self, text, parent=None):
        super(Chip, self).__init__(text, parent)

        self.clicked.connect(self.chip_clicked)

    def chip_clicked(self):
        print('chip clicked')
        print(self.text)

class MyLineEdit(QtWidgets.QLineEdit):
    focusIn = QtCore.Signal()
    focusOut = QtCore.Signal()
    keyPressed = QtCore.Signal(int)

    def focusInEvent(self, event):
        # print 'focus in event'
        # do custom stuff
        super(MyLineEdit, self).focusInEvent(event)
        self.focusIn.emit()

    def focusOutEvent(self, event):
        # print 'focus out event'
        # do custom stuff
        super(MyLineEdit, self).focusOutEvent(event)
        self.focusOut.emit()

    def keyPressEvent(self, event):
        super(MyLineEdit, self).keyPressEvent(event)
        self.keyPressed.emit(event.key())

class ChipsAutocomplete(QtWidgets.QDialog):
    items = []
    filteredItems = items
    selectedItems = []
    chips = []

    # set parent of widget as maya's main window
    # this means the widget will stay on top of maya
    def __init__(self, parent=None):
        super(ChipsAutocomplete, self).__init__(parent)

        self.setWindowTitle('Modal Dialogs')
        self.setMinimumSize(400,200)

        # remove help icon (question mark) from window
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        # create widgets, layouts and connections (signals and slots)
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.label = QtWidgets.QLabel('Chips')

        self.chip_list = QtWidgets.QListWidget()

        self.input = MyLineEdit()

        self.list = QtWidgets.QListWidget()
        self.list.addItems(self.items)
        self.list.hide()

        self.setFocus() # removes focus from the line edit

    def create_layouts(self):
        # self must be passed to the main_layout so it is parented to the dialog instance
        main_layout = QtWidgets.QVBoxLayout(self)

        main_layout.setAlignment(QtCore.Qt.AlignTop)

        widget_layout = QtWidgets.QVBoxLayout()
        widget_layout.setSpacing(0)

        self.chip_layout = QtWidgets.QHBoxLayout()

        input_layout = QtWidgets.QHBoxLayout()
        input_layout.addLayout(self.chip_layout)
        input_layout.addWidget(self.input)

        widget_layout.addLayout(input_layout)
        # widget_layout.addWidget(self.input2)
        widget_layout.addWidget(self.list)

        main_layout.addLayout(widget_layout)

    def create_connections(self):
        self.input.focusIn.connect(self.show_list)
        self.input.textChanged.connect(self.input_edited)
        self.input.keyPressed.connect(self.on_key_pressed)
        self.input.returnPressed.connect(self.input_enter_pressed)

        self.list.itemClicked.connect(self.item_selected)

    def addItems(self, items):
        self.items = items
        self.filteredItems = items
        self.selectedItems = []
        self.chips = []

        self.list.clear()
        self.list.addItems(items)

    def show_list(self):
        print('items:')
        print(self.items)
        print('filtered items:')
        print(self.filteredItems)
        print('selected items:')
        print(self.selectedItems)

        if self.items:
            self.list.show()
            print('show list')

    def hide_list(self):
        self.list.hide()

    def input_edited(self, text):
        # self.filteredItems = [s for s in self.items if text in s]

        # self.list.clear()
        # self.list.addItems(self.filteredItems)
        self.update_list(text)

    def update_list(self, text=None):
        #print(self.items)
        if not text:
            text = self.input.text()

        self.filteredItems = []

        for item in self.items:
            #print('checking item {}'.format(item))
            if text in item:
                #print('{} is in {}'.format(text,item))
                if not item in self.selectedItems:
                    #print('add item {}'.format(item))
                    self.filteredItems.append(item)
                else:
                    continue
                    print('ignoring {} since it is in selected items'.format(text))

        print('filtered items {}'.format(self.filteredItems))

        self.list.clear()
        self.list.addItems(self.filteredItems)

    def item_selected(self,item):
        self.add_chip(item.text())
        self.update_list()

    def input_enter_pressed(self):
        text = self.input.text()

        if text and not text in self.selectedItems:
            self.input.setText('')
            self.add_chip(text)

    def add_chip(self, text):
        self.selectedItems.append(text)

        wdg = QtWidgets.QPushButton(text)
        self.chips.append(wdg)
        self.chip_layout.addWidget(wdg)
        wdg.clicked.connect(lambda: self.chip_clicked(wdg))
        self.input.setFocus()

    def chip_clicked(self, widget):
        text = widget.text()
        if text in self.selectedItems:
            self.selectedItems.remove(text)
        else:
            return

        widget.deleteLater()
        widget = None
        self.update_list()

    def mousePressEvent(self, event):
        self.input.clearFocus() # clear focus from line edit
        self.list.hide()

    def keyPressEvent(self, event):
        key = event.key()

        if key == QtCore.Qt.Key_Down:
            self.list.item(0).setSelected(True)
            self.list.setCurrentRow(0)
            self.list.setFocus()
        elif key == QtCore.Qt.Key_Escape:
            self.input.clearFocus()
            self.list.hide()

    def on_key_pressed(self, key):
        numItems = self.list.count()

        if numItems == 0:
            return

        if key == QtCore.Qt.Key_Down:
            self.list.item(0).setSelected(True)
            self.list.setCurrentRow(0)
            self.list.setFocus()
        elif key == QtCore.Qt.Key_Up:
            self.list.item(numItems-1).setSelected(True)
            self.list.setCurrentRow(numItems-1)
            self.list.setFocus()

def run_standalone():
    app = QtWidgets.QApplication(sys.argv)

    my_dialog = ChipsAutocomplete()
    my_dialog.addItems(['apple', 'lemon', 'orange', 'mango', 'papaya', 'strawberry'])

    my_dialog.show()  # Show the UI
    sys.exit(app.exec_())

if __name__ == "__main__":
  run_standalone()
