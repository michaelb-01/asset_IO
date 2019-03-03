import sys
import os

from PySide2 import QtCore, QtWidgets, QtGui

sys.dont_write_bytecode = True  # Avoid writing .pyc files

import sqss_compiler
import TBA_UI

import tba_maya_api
#import maya.cmds as mc

import TBA_IO_chips
import TBA_IO_resources

class TBA_IO_properties(QtWidgets.QDialog):
    app = None
    assets = []

    def __init__(self, parent=None):
        super(TBA_IO_properties, self).__init__(parent)
        # unique object name for maya
        self.setObjectName('TBA_IO_properties')

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        self.setMinimumWidth(200)

        # self.setGeometry(100,100,300,300)

    def create_widgets(self):
        self.assetName = QtWidgets.QLabel('Asset ') 
        self.assetTask = QtWidgets.QLabel('Asset Task')
        self.assetVersion = QtWidgets.QLabel()
        self.author = QtWidgets.QLabel()
        self.dateUpdated = QtWidgets.QLabel()

        self.chips = TBA_IO_chips.ChipsAutocomplete()
        self.chips.addItems(['apple', 'lemon', 'orange', 'mango', 'papaya', 'strawberry'])

    def create_layouts(self):
        # self must be passed to the main_layout so it is parented to the dialog instance
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(2)
        main_layout.setContentsMargins(0,5,0,0)
        main_layout.setAlignment(QtCore.Qt.AlignTop)

        form_layout = QtWidgets.QFormLayout()
        form_layout.setFormAlignment(QtCore.Qt.AlignLeft)
        form_layout.setLabelAlignment(QtCore.Qt.AlignLeft)
        form_layout.addRow('Name', self.assetName)
        form_layout.addRow('Task', self.assetTask)
        form_layout.addRow('Author', QtWidgets.QLabel('Mike Battcock'))

        main_layout.addWidget(QtWidgets.QLabel('Properties'))
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.chips)

    def create_connections(self):
        pass

    def add_item_standalone(self):
        item = QtWidgets.QListWidgetItem('', self.list)
        item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEditable)
        item.setCheckState(QtCore.Qt.Checked)
        item.setSelected(True)
        self.list.editItem(item)

    def mousePressEvent(self, event):
        print('mouse press event')
        self.chips.hide_list()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    module_path = os.path.dirname(os.path.abspath(__file__))

    app.setStyleSheet(sqss_compiler.compile(
        os.path.join(module_path,'TBA_stylesheet.scss'),
        os.path.join(module_path,'variables.scss'),
    ))

    tba_io_properties = TBA_IO_properties()

    tba_io_properties.show()  # Show the UI
    sys.exit(app.exec_())
