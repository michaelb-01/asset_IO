import sys
import os

from PySide2 import QtCore, QtWidgets, QtGui

sys.dont_write_bytecode = True  # Avoid writing .pyc files

import sqss_compiler
import TBA_UI

from TBA_IO_collection_list import TBA_IO_collection_list
from TBA_IO_asset_list import TBA_IO_asset_list

from TBA_IO_object_list import TBA_IO_object_list
from TBA_IO_notes import TBA_IO_notes


class TBA_IO_exporter(QtWidgets.QDialog):
    importer = False

    def __init__(self, parent=None):
        super(TBA_IO_exporter, self).__init__(parent)

        # unique object name for maya
        self.setObjectName('TBA_IO_exporter')

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.collections = TBA_IO_collection_list()
        self.asset_list = TBA_IO_asset_list()

        module_path = os.path.dirname(os.path.abspath(__file__))
        workspace = os.path.join(module_path, 'vfx', 'shots', 'sh0001', 'maya')
        self.asset_list.set_workspace(workspace)

        self.object_list = TBA_IO_object_list()
        self.notes = TBA_IO_notes()
        pass

    def create_layouts(self):
        # self must be passed to the main_layout so it is parented to the dialog instance
        main_layout = QtWidgets.QHBoxLayout(self)

        col1_layout = QtWidgets.QVBoxLayout()
        col1_layout.addWidget(self.collections)
        col1_layout.addWidget(self.asset_list)

        col2_layout = QtWidgets.QVBoxLayout()
        col2_layout.addWidget(self.object_list)
        col2_layout.addWidget(self.notes)

        main_layout.addLayout(col1_layout)
        main_layout.addLayout(col2_layout)

        pass

    def create_connections(self):
        self.collections.list.clicked.connect(self.collection_clicked)
        pass

    def collection_clicked(self):
        print('collection_clicked, load objects')
        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    module_path = os.path.dirname(os.path.abspath(__file__))

    app.setStyleSheet(sqss_compiler.compile(
        os.path.join(module_path,'TBA_stylesheet.scss'),
        os.path.join(module_path,'variables.scss'),
    ))

    tba_io_export_options = TBA_IO_exporter()

    tba_io_export_options.show()  # Show the UI
    sys.exit(app.exec_())
