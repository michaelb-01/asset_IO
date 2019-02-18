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
from TBA_IO_export_options import TBA_IO_export_options

# ----------------------------------------------------------------------
# Environment detection
# ----------------------------------------------------------------------

try:
    import maya.cmds as mc
    import maya.OpenMayaUI as omui
    from shiboken2 import wrapInstance
    MAYA = True
except ImportError:
    MAYA = False

try:
    import nuke
    import nukescripts
    NUKE = True
except ImportError:
    NUKE = False

STANDALONE = False
if not MAYA and not NUKE:
    STANDALONE = True

class TBA_IO_exporter(QtWidgets.QDialog):
    dlg_instance = None

    @classmethod
    def show_dialog(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = TBA_IO_exporter(maya_main_window())

            module_path = os.path.dirname(os.path.abspath(__file__))

            cls.dlg_instance.setStyleSheet(sqss_compiler.compile(
                os.path.join(module_path,'TBA_stylesheet.scss'),
                os.path.join(module_path,'variables.scss'),
            ))

        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()

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

        self.export_options = TBA_IO_export_options()

        self.export_btn = QtWidgets.QPushButton('Export')
        self.export_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.export_btn.setProperty('stroke', True)

    def create_layouts(self):
        # self must be passed to the main_layout so it is parented to the dialog instance
        main_layout = QtWidgets.QVBoxLayout(self)

        main_layout.addWidget(self.asset_list)
        main_layout.addWidget(self.notes)
        main_layout.addWidget(self.export_options)

        main_layout.addWidget(self.export_btn)

    def create_connections(self):
        self.collections.list.clicked.connect(self.collection_clicked)
        pass

    def collection_clicked(self):
        print('collection_clicked, load objects')

# ----------------------------------------------------------------------
# DCC application helper functions
# ----------------------------------------------------------------------

def maya_main_window():
    # get pointer to maya's main window
    main_window_ptr = omui.MQtUtil.mainWindow()
    # return window as a QWidget
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

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
