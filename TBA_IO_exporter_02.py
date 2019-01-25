import sys
import os
import platform

sys.dont_write_bytecode = True  # Avoid writing .pyc files

import sqss_compiler
import TBA_UI

# ----------------------------------------------------------------------
# Environment detection
# ----------------------------------------------------------------------

try:
    import maya.cmds as cmds
    import maya.OpenMayaUI as omui
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



from PySide2 import QtCore, QtWidgets
from shiboken2 import wrapInstance

class TBAAssetExporter(QtWidgets.QDialog):
    STAGES = ['camera', 'model', 'anim', 'fx', 'rig', 'light', 'shaders']

    # set parent of widget as maya's main window
    # this means the widget will stay on top of maya
    def __init__(self, parent=None):
        super(TBAAssetExporter, self).__init__(parent)

        self.setWindowTitle('Modal Dialogs')
        self.setMinimumSize(300,80)

        # remove help icon (question mark) from window
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        # create widgets, layouts and connections (signals and slots)
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.assetName = QtWidgets.QLineEdit('Asset Name')

        self.assetListLabel = QtWidgets.QLabel('Assets')
        self.assetList = TBA_UI.TBA_list()

        self.stageListLabel = QtWidgets.QLabel('Stages')
        self.stageList = TBA_UI.TBA_list()

        self.versionListLabel = QtWidgets.QLabel('Versions')
        self.versionList = TBA_UI.TBA_list()

        self.notesLabel = QtWidgets.QLabel('Notes')
        self.notes = QtWidgets.QPlainTextEdit()
        self.notes.setFixedHeight(100)

        # asset type combobox
        self.stagesComboLabel = QtWidgets.QLabel('Stage')
        self.stagesCombo = QtWidgets.QComboBox()
        self.stagesCombo.addItems(self.STAGES)

        # format combobox
        self.formatsComboLabel = QtWidgets.QLabel('Format')
        self.formatsCombo = QtWidgets.QComboBox()

        # work range radio buttons
        self.rb_curFrame = QtWidgets.QRadioButton("Current Frame")
        self.rb_curFrame.setChecked(True)
        self.rb_workRange = QtWidgets.QRadioButton("Time Slider")
        self.rb_startEnd = QtWidgets.QRadioButton("Start End")

    def create_layouts(self):
        # self must be passed to the main_layout so it is parented to the dialog instance
        main_layout = QtWidgets.QVBoxLayout(self)

        main_layout.addWidget(self.assetName)

        # horizontal layout to hold asset and version list
        asset_list_master_layout = QtWidgets.QHBoxLayout()

        # asset list layout
        asset_list_layout = QtWidgets.QVBoxLayout()
        asset_list_layout.addWidget(self.assetListLabel)
        asset_list_layout.addWidget(self.assetList)

        # stages list layout
        stages_list_layout = QtWidgets.QVBoxLayout()
        stages_list_layout.addWidget(self.stageListLabel)
        stages_list_layout.addWidget(self.stageList)

        # version list layout
        version_list_layout = QtWidgets.QVBoxLayout()
        version_list_layout.addWidget(self.versionListLabel)
        version_list_layout.addWidget(self.versionList)

        asset_list_master_layout.addLayout(asset_list_layout)
        asset_list_master_layout.addLayout(stages_list_layout)
        asset_list_master_layout.addLayout(version_list_layout)

        # format dropdowns
        format_list_master_layout = QtWidgets.QHBoxLayout()

        stage_combo_layout = QtWidgets.QVBoxLayout()
        stage_combo_layout.addWidget(self.stagesComboLabel)
        stage_combo_layout.addWidget(self.stagesCombo)

        format_combo_layout = QtWidgets.QVBoxLayout()
        format_combo_layout.addWidget(self.formatsComboLabel)
        format_combo_layout.addWidget(self.formatsCombo)

        format_list_master_layout.addLayout(stage_combo_layout)
        format_list_master_layout.addLayout(format_combo_layout)

        # frame range layout
        frame_range_layout = QtWidgets.QVBoxLayout()
        frame_range_layout.addWidget(self.rb_curFrame)
        frame_range_layout.addWidget(self.rb_workRange)
        frame_range_layout.addWidget(self.rb_startEnd)

        main_layout.addLayout(asset_list_master_layout)
        main_layout.addWidget(self.notesLabel)
        main_layout.addWidget(self.notes)
        main_layout.addLayout(format_list_master_layout)
        main_layout.addLayout(frame_range_layout)

    def create_connections(self):
        pass


# ----------------------------------------------------------------------
# DCC application helper functions
# ----------------------------------------------------------------------

def maya_main_window():
    # get pointer to maya's main window
    main_window_ptr = omui.MQtUtil.mainWindow()
    # return window as a QWidget
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

def run_maya():
    print('TBA :: Run Maya')

    # for development purposes we want to delete any existing test_dialogs and recreate it
    # however for production it is better just to close and reopen the same instance without creating a new one

    # will only work if test_dialog has already been created and exists in Maya's main namespace
    try:
        my_dialog.close()
        my_dialog.deleteLater()
    except:
        pass

    my_dialog = MyDialog()
    my_dialog.show()


def run_standalone():
    print('TBA :: Run Standalone')
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(sqss_compiler.compile('TBA_stylesheet.scss', 'variables.scss'))
    #app.setStyleSheet("QLineEdit { background-color: yellow }")

    tba_exporter = TBAAssetExporter()

    tba_exporter.show()  # Show the UI
    sys.exit(app.exec_())

if __name__ == "__main__":
    if MAYA:
        run_maya()
    elif NUKE:
        run_nuke()
    else:
        run_standalone()


