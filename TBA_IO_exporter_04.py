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

import TBA_IO_resources
import tba_utils
import tba_utils_maya

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
    app = APP

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

    tasks = ['model','layout','rig','anim','lookDev','light']

    @classmethod
    def show_dialog(cls):
        if not cls.dlg_instance:
            print('TBA :: TBA_IO_exporter - initialise new instance!')
            cls.dlg_instance = TBA_IO_exporter(maya_main_window())

            module_path = os.path.dirname(os.path.abspath(__file__))

            cls.dlg_instance.setStyleSheet(sqss_compiler.compile(
                os.path.join(module_path, 'TBA_stylesheet.scss'),
                os.path.join(module_path, 'variables.scss'),
            ))

        if cls.dlg_instance.isHidden():
            print('TBA :: TBA_IO_exporter - show')
            cls.dlg_instance.show()
        else:
            print('TBA :: TBA_IO_exporter - raise')
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()


    def __init__(self, parent=None):
        super(TBA_IO_exporter, self).__init__(parent)
        print('PARENT IS')
        print(parent)

        # unique object name for maya
        self.setObjectName('TBA_IO_exporter')

        self.setProperty("saveWindowPref", True)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        '''
        if APP == 'maya':
            self.update_maya_workspace()
        else:
            module_path = os.path.dirname(os.path.abspath(__file__))
            workspace = os.path.join(module_path, 'vfx', 'shots', 'sh0001', 'maya')
            self.asset_list.set_workspace(workspace)
        '''

    def create_widgets(self):
        # self.asset_list = TBA_IO_asset_list()

        self.task = QtWidgets.QComboBox()
        self.task.addItems(self.tasks)

        self.collection_list = TBA_IO_collection_list(app=self.app)

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

        main_layout.addWidget(self.task)

        main_layout.addWidget(self.collection_list)
        # main_layout.addWidget(self.asset_list)
        main_layout.addWidget(self.notes)
        main_layout.addWidget(self.export_options)

        export_layout = QtWidgets.QHBoxLayout()
        export_layout.addWidget(self.export_separate_cb)
        export_layout.addWidget(self.export_btn)

        main_layout.addLayout(export_layout)

    def create_connections(self):
        self.export_btn.clicked.connect(self.export)

    def export_abc(self, asset):
        print('export_abc')
        print(asset)

        tba_utils_maya.export_abc(asset)

        # msg = QtWidgets.QMessageBox()
        # msg.setIcon(QMessageBox.Information)
        # msg.setText("Export Successfull")
        # msg.setInformativeText(asset['filepath'])

    def export_to_database(self, asset):
        # tba_utils.test()
        tba_utils.db.export_asset(asset)

    def export(self):
        print('export!!')
        collections = self.collection_list.list

        # get data
        data = tba_utils.parse_job_path(tba_utils_maya.get_scene_path())
        publish_path = os.path.join(data['job_path'], 'vfx', data['stage'], '_published3d')

        # exported objects
        exported = []

        for i in range(collections.count()):
            item = collections.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                asset = item.data(QtCore.Qt.UserRole)

                version = 'v' + str(asset['version'] + 1).zfill(3)
                asset['filepath'] = os.path.join(publish_path, asset['name'], asset['type'], version, asset['name'] + '.abc' )

                success = self.export_abc(asset)

                if success:
                    exported.append(asset)

                self.export_to_database(asset)

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

