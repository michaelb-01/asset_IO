import sys
import os

from PySide2 import QtCore, QtWidgets, QtGui

import sqss_compiler
import TBA_UI

from TBA_IO_collection_list import TBA_IO_collection_list
from TBA_IO_asset_list import TBA_IO_asset_list

from TBA_IO_object_list import TBA_IO_object_list
from TBA_IO_notes import TBA_IO_notes
from TBA_IO_export_options import TBA_IO_export_options

sys.dont_write_bytecode = True  # Avoid writing .pyc files

# ----------------------------------------------------------------------
# Environment detection
# ----------------------------------------------------------------------

APP = 'standalone'

try:
    import maya.cmds as mc
    import tba_maya_api
    import maya.OpenMayaUI as omui
    from shiboken2 import wrapInstance
    APP = 'maya'
except ImportError:
    pass

try:
    import nuke
    import nukescripts
    APP = 'nuke'
except ImportError:
    pass

class TBA_IO_exporter(QtWidgets.QDialog):
    dlg_instance = None

    # job root
    jobroot = ''

    # maya/nuke/houdini project folder
    workspace = ''

    software = ''

    stage = ''
    entity = ''

    # export and publish dirs
    export_dir = ''
    publish_dir = ''

    @classmethod
    def show_dialog(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = TBA_IO_exporter(maya_main_window())

            module_path = os.path.dirname(os.path.abspath(__file__))

            cls.dlg_instance.setStyleSheet(sqss_compiler.compile(
                os.path.join(module_path, 'TBA_stylesheet.scss'),
                os.path.join(module_path, 'variables.scss'),
            ))

        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()


    def __init__(self, parent=None):
        super(TBA_IO_exporter, self).__init__(parent)
        print('PARENT IS')
        print(parent)

        # unique object name for maya
        self.setObjectName('TBA_IO_exporter')

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        if APP == 'maya':
            self.update_maya_workspace()
        else:
            module_path = os.path.dirname(os.path.abspath(__file__))
            workspace = os.path.join(module_path, 'vfx', 'shots', 'sh0001', 'maya')
            self.asset_list.set_workspace(workspace)

    def create_widgets(self):
        self.asset_list = TBA_IO_asset_list()
        self.collection_list = TBA_IO_collection_list()
        self.object_list = TBA_IO_object_list()
        self.notes = TBA_IO_notes()

        self.export_options = TBA_IO_export_options()

        self.export_btn = QtWidgets.QPushButton('Export')
        self.export_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.export_btn.setProperty('stroke', True)

        self.export_separate_cb = QtWidgets.QCheckBox('Export Per Selection')
        self.export_separate_cb.setCursor(QtCore.Qt.PointingHandCursor)

    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        main_layout.addWidget(self.collection_list)
        main_layout.addWidget(self.asset_list)
        main_layout.addWidget(self.notes)
        main_layout.addWidget(self.export_options)

        export_layout = QtWidgets.QHBoxLayout()
        export_layout.addWidget(self.export_separate_cb)
        export_layout.addWidget(self.export_btn)

        main_layout.addLayout(export_layout)

    def create_connections(self):
        self.export_btn.clicked.connect(self.export)

    def export(self):
        tba_maya_api.export_selected()
        print('export!!')

    def update_maya_workspace(self):
        workspace = mc.workspace(q=1,fullName=1)

        print('TBA :: workspace is: {0}'.format(workspace))

        self.asset_list.set_workspace(workspace)

# ----------------------------------------------------------------------
# DCC application helper functions
# ----------------------------------------------------------------------

def maya_main_window():
    # get pointer to maya's main window
    main_window_ptr = omui.MQtUtil.mainWindow()
    # return window as a QWidget
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

def run_standalone():
    app = QtWidgets.QApplication(sys.argv)

    module_path = os.path.dirname(os.path.abspath(__file__))

    app.setStyleSheet(sqss_compiler.compile(
        os.path.join(module_path, 'TBA_stylesheet.scss'),
        os.path.join(module_path, 'variables.scss'),
    ))

    tba_io_export_options = TBA_IO_exporter()

    tba_io_export_options.show()  # Show the UI
    sys.exit(app.exec_())

if __name__ == "__main__":
    if APP == 'maya':
        run_maya()
    elif APP == 'nuke':
        run_nuke()
    else:
        run_standalone()

