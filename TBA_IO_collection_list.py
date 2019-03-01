import sys
import os

from PySide2 import QtCore, QtWidgets, QtGui

sys.dont_write_bytecode = True  # Avoid writing .pyc files

import sqss_compiler
import TBA_UI

import tba_maya_api
#import maya.cmds as mc

import TBA_IO_resources
import TBA_IO_chips

class TBA_IO_collection_list(QtWidgets.QDialog):
    importer = False
    cbIds = []

    app = None

    def __init__(self, parent=None, app=None):
        super(TBA_IO_collection_list, self).__init__(parent)
        self.app = app

        # unique object name for maya
        self.setObjectName('TBA_IO_collection_list')

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        #self.refresh()

    def create_widgets(self):
        self.header = QtWidgets.QLabel('Collections')
        self.header.setAlignment(QtCore.Qt.AlignTop)
        self.header.setFixedHeight(24)

        self.list = QtWidgets.QListWidget()

        self.chips = TBA_IO_chips.ChipsAutocomplete()
        self.chips.addItems(['apple', 'lemon', 'orange', 'mango', 'papaya', 'strawberry'])

        self.add_btn = QtWidgets.QPushButton('+')
        self.add_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.add_btn.setStyleSheet('QPushButton { font-size: 20px; width:24px; height:24px; margin:0; padding:0 0 4 1;}')

        self.list.setStyleSheet('''
                                    QListWidget {
                                        padding: 1px;
                                    }
                                    QListWidget::item {
                                        background-color: rgb(80,85,95);
                                        height: 25px;
                                        margin: 0;
                                        padding: 0;
                                        border-bottom: 1px solid #333;
                                    }
                                    QListWidget::item:selected {
                                        background-color: rgba(207,66,53,0.5);
                                    }
                                    ''')

    def create_layouts(self):
        # self must be passed to the main_layout so it is parented to the dialog instance
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setSpacing(2)
        main_layout.setContentsMargins(0,0,0,0)

        list_layout = QtWidgets.QVBoxLayout()

        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setContentsMargins(0,0,0,0)

        header_layout.addWidget(self.header)
        header_layout.addStretch()
        header_layout.addWidget(self.add_btn)
        header_layout.setAlignment(QtCore.Qt.AlignTop)

        list_layout.addLayout(header_layout)
        list_layout.addWidget(self.list)

        property_layout = QtWidgets.QVBoxLayout()
        property_layout.addWidget(self.chips)

        main_layout.addLayout(list_layout)
        main_layout.addLayout(property_layout)

    def create_connections(self):
        if (self.app == 'maya'):
            self.add_btn.clicked.connect(self.add_item_maya)
        else:
            self.add_btn.clicked.connect(self.add_item_standalone)

    def refresh(self):
        print('TBA_IO_collection_list - refresh_list')

        #cbIds.extend(tba_maya_api.set_asset_callbacks())

        tba_assets = tba_maya_api.get_maya_assets()

        self.list.clear()

        for name in tba_assets:
            item = QtWidgets.QListWidgetItem(name, self.list)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEditable)
            item.setCheckState(QtCore.Qt.Checked)

    def add_item_maya(self):
        tba_sets = tba_maya_api.create_tba_sets()

        for tba_set in tba_sets:
            item = QtWidgets.QListWidgetItem(tba_set, self.list)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEditable)
            item.setCheckState(QtCore.Qt.Checked)

        # item = QtWidgets.QListWidgetItem('', self.list)
        # item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEditable)
        # item.setCheckState(QtCore.Qt.Checked)
        # item.setSelected(True)
        # self.list.editItem(item)

    def add_item_standalone(self):
        item = QtWidgets.QListWidgetItem('', self.list)
        item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEditable)
        item.setCheckState(QtCore.Qt.Checked)
        item.setSelected(True)
        self.list.editItem(item)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    module_path = os.path.dirname(os.path.abspath(__file__))

    app.setStyleSheet(sqss_compiler.compile(
        os.path.join(module_path,'TBA_stylesheet.scss'),
        os.path.join(module_path,'variables.scss'),
    ))

    tba_io_collection_list = TBA_IO_collection_list()

    tba_io_collection_list.show()  # Show the UI
    sys.exit(app.exec_())
