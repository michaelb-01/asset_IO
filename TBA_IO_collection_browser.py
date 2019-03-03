import sys
import os

from PySide2 import QtCore, QtWidgets, QtGui

sys.dont_write_bytecode = True  # Avoid writing .pyc files

import sqss_compiler
import TBA_UI

import TBA_IO_collection_list
import TBA_IO_properties
import tba_maya_api
#import maya.cmds as mc

class TBA_IO_collection_browser(QtWidgets.QDialog):
    importer = False
    cbIds = []

    app = None

    def __init__(self, parent=None, app=None):
        super(TBA_IO_collection_browser, self).__init__(parent)
        self.app = app

        # unique object name for maya
        self.setObjectName('TBA_IO_collection_browser')

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        #self.refresh()
        self.resize(300,300)

    def create_widgets(self):
        self.collection_list = TBA_IO_collection_list.TBA_IO_collection_list()
        self.properties = TBA_IO_properties.TBA_IO_properties()

    def create_layouts(self):
        # self must be passed to the main_layout so it is parented to the dialog instance
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setSpacing(2)
        main_layout.setContentsMargins(0,0,0,0)

        main_layout.addWidget(self.collection_list)
        main_layout.addWidget(self.properties)

    def create_connections(self):
        pass

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

    tba_io_collection_browser = TBA_IO_collection_browser()

    tba_io_collection_browser.show()  # Show the UI
    sys.exit(app.exec_())
