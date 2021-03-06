import sys
import os
import platform
import re
import json
import subprocess
import getpass
import shutil

sys.dont_write_bytecode = True  # Avoid writing .pyc files

import sqss_compiler
import TBA_UI

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

from PySide2 import QtCore, QtWidgets, QtGui

class TBAExportResultsDialog(QtWidgets.QDialog):
    def __init__(self, exportResults, parent=None):
        super(TBAExportResultsDialog, self).__init__(parent)

        module_path = os.path.dirname(os.path.abspath(__file__))

        self.setStyleSheet(sqss_compiler.compile(
            os.path.join(module_path,'TBA_stylesheet.scss'),
            os.path.join(module_path,'variables.scss'),
        ))

        self.exportResults = exportResults
        self.platform = sys.platform

        self.setWindowTitle("Custom Dialog")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.export_label = QtWidgets.QLabel('Export Successfull')
        self.export_browse_btn = QtWidgets.QPushButton('Open')

        self.publish_label = QtWidgets.QLabel('Publish Successfull')
        self.publish_browse_btn = QtWidgets.QPushButton('Open')

        self.ok_btn = QtWidgets.QPushButton('Ok')

    def create_layout(self):
        export_layout = QtWidgets.QHBoxLayout()
        export_layout.addWidget(self.export_label)
        export_layout.addWidget(self.export_browse_btn)

        main_layout = QtWidgets.QVBoxLayout(self)

        main_layout.addLayout(export_layout)

        if len(self.exportResults) > 1:
            publish_layout = QtWidgets.QHBoxLayout()
            publish_layout.addWidget(self.publish_label)
            publish_layout.addWidget(self.publish_browse_btn)

            main_layout.addLayout(publish_layout)

    def create_connections(self):
        self.export_browse_btn.clicked.connect(lambda: self.exploreFile(0))
        self.publish_browse_btn.clicked.connect(lambda: self.exploreFile(1))

    def exploreFile(self, which):
        if self.platform == "win32":
            print('Explore file in windows explorer')
            subprocess.Popen(r'explorer /select, ' + self.exportResults[which])
        elif self.platform == "darwin":
            print('Explore file in max finder')
            subprocess.Popen(["open", self.exportResults[which]])
        else:
            print('OS is linux, ignoring..')

class TBAAssetExporter(QtWidgets.QDialog):
    PLATFORM = sys.platform

    TYPES = ['camera', 'model', 'anim', 'fx', 'rig', 'light', 'shaders']
    DARK_COLOUR = QtGui.QColor(80,85,95)
    PRIMARY = 'rgb(207,66,53)'
    SECONDARY = 'rgb(64, 162, 153)'

    FORMATS = {
        'camera':['abc','fbx','mb'],
        'model':['abc','obj','fbx','mb'],
        'anim':['abc','fbx','mb'],
        'fx':['abc','mb'],
        'rig':['mb'],
        'light':['mb']
    }

    importer = False

    publishDirName = '_published3d'
    exportDirName = 'exports'   # could be different for maya/nuke/houdini

    exportDir = None
    publishDir = None
    selAsset = None
    selType = None
    selVersion = None

    tempAsset = False

    dlg_instance = None

    @classmethod
    def show_dialog(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = TBAAssetExporter(maya_main_window())

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

    # set parent of widget as maya's main window
    # this means the widget will stay on top of maya
    def __init__(self, parent=None):
        super(TBAAssetExporter, self).__init__(parent)
        print('TBA Asset Exporter')
        print(parent)

        self.setWindowTitle('Modal Dialogs')
        self.setMinimumSize(300,80)

        # remove help icon (question mark) from window
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.getExportDir()

        # create widgets, layouts and connections (signals and slots)
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        self.resize(500,600)

    def create_widgets(self):
        self.assetNameLabel = QtWidgets.QLabel('Asset Name')
        self.assetName = QtWidgets.QLineEdit('')

        self.assetListLabel = QtWidgets.QLabel('Assets')
        self.assetList = TBA_UI.TBA_list()
        # self.assetList.tbaList.addItems(['one','two','three'])
        self.updateAssetList()

        self.typesListLabel = QtWidgets.QLabel('Asset Types')
        self.typesList = TBA_UI.TBA_list()
        for type in self.FORMATS:
            item = QtWidgets.QListWidgetItem(type)
            self.disableItem(item)
            self.typesList.tbaList.addItem(item)

        self.versionListLabel = QtWidgets.QLabel('Versions')
        self.versionList = TBA_UI.TBA_list()

        self.versionAutoVersion = QtWidgets.QCheckBox()
        self.versionAutoVersion.setChecked(True)
        self.versionAutoVersion.setToolTip('Auto-version')

        self.versionList.setFooter('v001')

        self.notesLabel = QtWidgets.QLabel('Notes')
        self.notes = QtWidgets.QPlainTextEdit()
        self.notes.setFixedHeight(100)

        # asset type combobox
        self.typesComboLabel = QtWidgets.QLabel('Asset Types')
        self.typesCombo = QtWidgets.QComboBox()
        for type in self.FORMATS:
            self.typesCombo.addItem(type)

        # format combobox
        self.formatsComboLabel = QtWidgets.QLabel('Format')
        self.formatsCombo = QtWidgets.QComboBox()

        # work range radio buttons
        self.rb_curFrame = QtWidgets.QRadioButton("Current Frame")
        self.rb_curFrame.setChecked(True)
        self.rb_workRange = QtWidgets.QRadioButton("Time Slider")
        self.rb_startEnd = QtWidgets.QRadioButton("Start End")

        self.range_start_le = QtWidgets.QLineEdit('1001')
        self.range_start_le.setValidator(QtGui.QIntValidator()) # only allow integers
        self.range_start_le.setDisabled(True)

        self.range_end_le = QtWidgets.QLineEdit('1201')
        self.range_end_le.setValidator(QtGui.QIntValidator())
        self.range_end_le.setDisabled(True)

        self.range_step_le = QtWidgets.QLineEdit('1.0')
        self.range_step_le.setDisabled(True)

        # export
        self.publish_cb = QtWidgets.QCheckBox('Publish')

        self.export_btn = QtWidgets.QPushButton('Export')
        self.export_btn.setObjectName('export_button')
        self.export_btn.setEnabled(False)

    def create_layouts(self):
        # self must be passed to the main_layout so it is parented to the dialog instance
        main_layout = QtWidgets.QVBoxLayout(self)

        main_layout.addWidget(self.assetNameLabel)
        main_layout.addWidget(self.assetName)

        # horizontal layout to hold asset and version list
        asset_list_master_layout = QtWidgets.QHBoxLayout()

        # asset list layout
        asset_list_layout = QtWidgets.QVBoxLayout()
        asset_list_layout.addWidget(self.assetListLabel)
        asset_list_layout.addWidget(self.assetList)

        # stages list layout
        types_list_layout = QtWidgets.QVBoxLayout()
        types_list_layout.addWidget(self.typesListLabel)
        types_list_layout.addWidget(self.typesList)

        # version list layout
        version_list_layout = QtWidgets.QVBoxLayout()

        version_list_header_layout = QtWidgets.QHBoxLayout()

        version_list_header_layout.addWidget(self.versionListLabel)
        version_list_header_layout.addStretch()
        version_list_header_layout.addWidget(self.versionAutoVersion)

        version_list_layout.addLayout(version_list_header_layout)
        version_list_layout.addWidget(self.versionList)

        asset_list_master_layout.addLayout(asset_list_layout)
        asset_list_master_layout.addLayout(types_list_layout)
        asset_list_master_layout.addLayout(version_list_layout)

        # format dropdowns
        format_list_master_layout = QtWidgets.QHBoxLayout()

        types_combo_layout = QtWidgets.QVBoxLayout()
        types_combo_layout.addWidget(self.typesComboLabel)
        types_combo_layout.addWidget(self.typesCombo)

        format_combo_layout = QtWidgets.QVBoxLayout()
        format_combo_layout.addWidget(self.formatsComboLabel)
        format_combo_layout.addWidget(self.formatsCombo)

        format_list_master_layout.addLayout(types_combo_layout)
        format_list_master_layout.addLayout(format_combo_layout)

        # frame range layout
        frame_range_rb_layout = QtWidgets.QVBoxLayout()
        frame_range_rb_layout.addWidget(self.rb_curFrame)
        frame_range_rb_layout.addWidget(self.rb_workRange)

        frame_range_layout = QtWidgets.QHBoxLayout()
        frame_range_layout.addWidget(self.rb_startEnd)
        frame_range_layout.addWidget(self.range_start_le)
        frame_range_layout.addWidget(self.range_end_le)
        frame_range_layout.addWidget(self.range_step_le)

        frame_range_rb_layout.addLayout(frame_range_layout)

        main_layout.addLayout(asset_list_master_layout)
        main_layout.addWidget(self.notesLabel)
        main_layout.addWidget(self.notes)
        main_layout.addLayout(format_list_master_layout)
        main_layout.addLayout(frame_range_rb_layout)

        export_options_layout = QtWidgets.QHBoxLayout()
        export_options_layout.addWidget(self.publish_cb)

        main_layout.addLayout(export_options_layout)
        main_layout.addWidget(self.export_btn)

    def create_connections(self):
        self.assetName.textChanged.connect(self.updateTempAssetName)

        # asset list
        self.assetList.tbaList.itemSelectionChanged.connect(self.onAssetSelected)
        self.assetList.rightClicked.connect(self.assetRightClicked)

        self.typesList.tbaList.itemSelectionChanged.connect(self.onTypeSelected)
        self.typesList.rightClicked.connect(self.assetRightClicked)
        self.typesCombo.currentIndexChanged.connect(self.onTypeComboSelected)

        self.versionList.tbaList.itemSelectionChanged.connect(self.onVersionSelected)
        self.versionList.rightClicked.connect(self.assetRightClicked)
        self.versionAutoVersion.toggled.connect(self.onAutoVersionChanged)


        self.rb_startEnd.toggled.connect(self.onRangeToggled)

        self.export_btn.clicked.connect(self.export)

    def getExportDir(self):
        # this function would look up the _published3d directory relative to the scene
        if MAYA:
            currentDir = mc.workspace(q=1,fullName=1)
        else:
            currentDir = os.path.dirname(os.path.realpath(__file__))

        self.exportDir = os.path.join(currentDir, self.exportDirName)
        self.publishDir = os.path.join(currentDir, '..', self.publishDirName)

        print('Export directory is: {0}'.format(self.exportDir))
        print('Publish directory is: {0}'.format(self.publishDir))

    def getAssetPath(self):
        path = os.path.join(self.exportDir, 'assets')

        # if version item is selected just delete this version
        if self.versionList.tbaList.hasFocus():
            selVersion = self.versionList.tbaList.currentItem().text()
            path = os.path.join(path, self.selAsset, self.selType, selVersion)
        # if type item is selected delete the asset type
        elif self.typesList.tbaList.hasFocus():
            path = os.path.join(path, self.selAsset, self.selType)
        elif self.assetList.tbaList.hasFocus():
            path = os.path.join(path, self.selAsset)
        else:
            return False

        return path

    # ----------------------------------------------------------------------
    # ASSET LIST LOGIC
    # ----------------------------------------------------------------------
    def assetRightClicked(self, pos):
        print('RECEIVED ASSET RIGHT CLICKED')

        contextMenu = QtWidgets.QMenu(self)

        deleteAct = contextMenu.addAction('Delete')
        exploreAct = contextMenu.addAction('Explore')

        action = contextMenu.exec_(pos)

        if action == deleteAct:
            self.deleteAsset()
        elif action == exploreAct:
            print('explore asset')
            self.exploreFile(0)

    def updateTempAssetName(self,name):
        print('updateTempAssetName: {0}'.format(name))
        name = self.camelCase(name)
        print('updateTempAssetName, camelCase name: {0}'.format(name))

        if not name:
            print('updateTempAssetName: removeTempAsset')
            self.removeTempAsset()
            self.assetList.tbaList.setFocus()
            return
        elif name.strip():
            self.selAsset = name
            items = self.assetList.tbaList.findItems(name, QtCore.Qt.MatchExactly)

            # remove temp asset if an asset on disk exists with the same name
            if items:
                # only if the asset in assetList is not the same as assetName. This can happen since we are stripping whitespace
                data = items[0].data(QtCore.Qt.UserRole)
                if data != 'temp':
                    print('updateTempAssetName, REMOVE ASSET NAME')
                    self.removeTempAsset()
                    self.assetList.tbaList.setCurrentItem(items[0])
            else:
                self.addTempAsset(name)

    def addTempAsset(self, e):
        # set temp asset item with user data
        print('addTempAsset: {0}'.format(e))

        # check if temp item already exists
        idx = 0
        for i in range(self.assetList.tbaList.count()):
            data = self.assetList.tbaList.item(i).data(QtCore.Qt.UserRole)
            idx += 1
            if data == 'temp':
                self.assetList.tbaList.item(i).setText(e)
                return False

        self.tempAsset = True

        # add list item with temp user data
        item = QtWidgets.QListWidgetItem(e)
        item.setData(QtCore.Qt.UserRole, 'temp')

        # change background-color to illustrate that this has not yet been created on disk
        self.assetList.tbaList.setStyleSheet('QListWidget::item:selected { background-color: ' + str(self.SECONDARY) + ' }')

        self.assetList.tbaList.addItem(item)
        self.assetList.tbaList.setCurrentRow(idx)

    def removeTempAsset(self):
        print('removeTempAsset')

        # remove item from asset list with userdata 'temp'

        for i in range(self.assetList.tbaList.count()):
            print('Check asset {0}'.format(self.assetList.tbaList.item(i).text()))
            data = self.assetList.tbaList.item(i).data(QtCore.Qt.UserRole)
            if data == 'temp':
                print('Remove item at {0}'.format(i))
                self.tempAsset = False

                # set selected row before deleting, otherwise seg fault
                self.assetList.tbaList.setCurrentRow(i-1)
                item = self.assetList.tbaList.takeItem(i)
                item = None

        # reset selected color to original
        self.assetList.tbaList.setStyleSheet('QListWidget::item:selected { background-color: ' + str(self.PRIMARY) + ' }')

    def onAssetSelected(self):
        print('onAssetSelected')
        item = self.assetList.tbaList.currentItem()

        if not self.assetList.tbaList.selectedItems():
            print('onAssetSelected: set selAsset to None')
            self.selAsset = None
            self.enable_export(False)
        else:
            self.selAsset = item.text()
            print('onAssetSelected: set selAsset to {0}'.format(self.selAsset))

        # remove temp item (as long as its not the temp item itself)
        if item:
            if item.data(QtCore.Qt.UserRole) != 'temp' and self.tempAsset:
                self.removeTempAsset()

        self.updateTypeList()
        self.enable_export(True)

    def updateAssetList(self):
        print('updateAssetList')
        # store item if currently selected
        selAsset = self.assetList.tbaList.currentItem()

        if selAsset:
            print('set selAsset to its text')
            selAsset = selAsset.text()

        print(selAsset)

        # clear all items, will repopulate later in this function
        self.assetList.tbaList.clear()

        # get assets from dir
        exportedAssetsDir = os.path.join(self.exportDir, 'assets')
        publishedAssetsDir = os.path.join(self.publishDir, 'assets')

        exportedAssets = []
        publishedAssets = []

        # check directories exist then get assets
        if os.path.exists(exportedAssetsDir):
            exportedAssets = sorted(os.listdir(exportedAssetsDir))
        else:
            print('Assets exports directory does not exist: {0}'.format(exportedAssetsDir))

        if os.path.exists(publishedAssetsDir):
            publishedAssets = sorted(os.listdir(publishedAssetsDir))
        else:
            print('Assets _published3d directory does not exist: {0}'.format(publishedAssetsDir))

        # add assets to asset list
        for asset in exportedAssets:
            # ignore hidden files
            if asset.startswith('.'):
                continue

            item = QtWidgets.QListWidgetItem(asset)

            if asset == selAsset:
                item.setSelected(True)

            self.assetList.tbaList.addItem(item)

            if asset not in publishedAssets:
                self.italicItem(item)

            # reselect item if it was selected
            if asset == selAsset:
                print('updateAssetList, asset == selAsset, setcurrentItem')
                self.assetList.tbaList.setCurrentItem(item)

    # ----------------------------------------------------------------------
    # TYPE LIST LOGIC
    # ----------------------------------------------------------------------
    def updateTypeList(self):
        print('updateTypeList')

        if not self.selAsset:
            print('updateTypeList, disableAllTypes')
            self.disableAllTypes()
            return

        # exported assets directory
        exportedAssetDir = os.path.join(self.exportDir, 'assets', self.selAsset)
        # published assets directory
        publishedAssetDir = os.path.join(self.publishDir, 'assets', self.selAsset)

        # if asset path does not exist
        if not os.path.isdir(exportedAssetDir):
            self.disableAllTypes()
            return

        # list folders inside assetDir
        exportedTypes = sorted(os.listdir(exportedAssetDir))

        if not os.path.isdir(publishedAssetDir):
            publishedTypes = []
        else:
            publishedTypes = sorted(os.listdir(publishedAssetDir))

        # iterate over types and disable if not found
        for i in range(self.typesList.tbaList.count()):
            item = self.typesList.tbaList.item(i)

            # if we are in the importer set the selectability of the item
            # else just change the colour to illustrate what has already been exported
            if item.text() in exportedTypes:
                self.enableItem(item)
                if item.text() not in publishedTypes:
                    self.italicItem(item)
            else:
                if self.importer:
                    self.disableItem(item)
                else:
                    self.darkenItem(item)

        # update the version list
        self.updateVersionList()

    def disableAllTypes(self):
        print('disableAllTypes')
        # disable all type items
        if self.importer:
            for i in range(self.typesList.tbaList.count()):
                self.disableItem(self.typesList.tbaList.item(i))
        else:
            for i in range(self.typesList.tbaList.count()):
                self.darkenItem(self.typesList.tbaList.item(i))

    def onTypeSelected(self):
        print('onTypeSelected')

        item = self.typesList.tbaList.currentItem()
        print('onTypeSelected, type:')
        print(item)

        if item:
            self.selType = item.text()

        self.updateVersionList()
        self.updateFormatList()

        # select type in combobox
        index = self.typesCombo.findText(self.selType, QtCore.Qt.MatchFixedString)
        if index >= 0:
             self.typesCombo.setCurrentIndex(index)

    def onTypeComboSelected(self, idx):
        print('onTypeComboSelected')

        self.typesList.tbaList.item(idx).setSelected(True)

        self.selType = self.typesCombo.itemText(idx)
        self.updateVersionList()
        self.updateFormatList()

    # ----------------------------------------------------------------------
    # VERSION LIST LOGIC
    # ----------------------------------------------------------------------

    def onVersionSelected(self):
        print('onVersionSelected')
        item = self.versionList.tbaList.currentItem()

        if not self.versionList.tbaList.selectedItems():
            self.selVersion = None
            return

        self.selVersion = item.text()

        if not self.versionList.footer:
            return

        self.versionList.footer.setText(item.text())

    def updateVersionList(self):
        print('updateVersionList')

        # clear all items, will repopulate later in this function
        self.versionList.tbaList.clear()

        # if no type is selected remove all versions from the list and return
        if not self.typesList.tbaList.selectedItems():
            print('no type selected')
            self.selVersion = None
            self.updateWriteVersion()
            return

        # versions directory
        exportedVersionsDir = os.path.join(self.exportDir, 'assets', self.selAsset, self.selType)
        publishedVersionsDir = os.path.join(self.publishDir, 'assets', self.selAsset, self.selType)

        # if version directory does not exist clear and return
        if not os.path.isdir(exportedVersionsDir):
            print('Version does not exist')
            self.updateWriteVersion()
            return

        # list version folders inside exportedVersionsDir
        exportedVersions = sorted(os.listdir(exportedVersionsDir))
        publishedVersions = []

        if os.path.isdir(publishedVersionsDir):
            publishedVersions = sorted(os.listdir(publishedVersionsDir))

        # iterate over folders and add to version list if named correctly
        for version in exportedVersions:
            # folder must match format of 'v' then three digits, e.g. v007
            if re.match("v[0-9]{3}", version):
                item = QtWidgets.QListWidgetItem(version)
                self.versionList.tbaList.addItem(item)
                if version not in publishedVersions:
                    self.italicItem(item)

        if self.versionAutoVersion.isChecked():
            self.disableAllVersions()

        self.updateWriteVersion()

        # update versions header
        #self.versionList.updateNumItems()

    def onAutoVersionChanged(self, checked):
        print('onAutoVersionChanged')

        if checked:
            self.disableAllVersions()
            self.selVersion = None
            self.typesList.tbaList.setFocus()
        else:
            self.enableAllVersions()

        self.updateWriteVersion()

    def updateWriteVersion(self):
        print('updateWriteVersion')

        writeVersion = self.versionList.footer.text()

        count = self.versionList.tbaList.count()

        # if auto version is checked take the latest version + 1
        if self.versionAutoVersion.isChecked():
            if count > 0:
                lastVersion = self.versionList.tbaList.item(count-1).text()
                try:
                    num = int(lastVersion[1:]) + 1
                    writeVersion = 'v' + str(num).zfill(3)
                except:
                    print('couldnt extract version number')
            else:
                writeVersion = 'v001'
        else:
            if count > 0:
                print('updateWriteVersion, versionList current item: ')
                print(self.versionList.tbaList.currentItem())

        self.versionList.setFooter(writeVersion)

    def disableAllVersions(self):
        print('disableAllVersions')
        for i in range(self.versionList.tbaList.count()):
            self.disableItem(self.versionList.tbaList.item(i))

    def enableAllVersions(self):
        print('disableAllVersions')
        for i in range(self.versionList.tbaList.count()):
            self.enableItem(self.versionList.tbaList.item(i))

    # ----------------------------------------------------------------------
    # FORMATS
    # ----------------------------------------------------------------------
    def updateFormatList(self):
        print('updateFormatList')
        self.formatsCombo.clear()

        formats = self.FORMATS[self.selType]

        self.formatsCombo.addItems(formats)

    # ----------------------------------------------------------------------
    # WORK RANGE
    # ----------------------------------------------------------------------
    def onRangeToggled(self, checked):
        self.range_start_le.setDisabled(not checked)
        self.range_end_le.setDisabled(not checked)
        self.range_step_le.setDisabled(not checked)

    # ----------------------------------------------------------------------
    # EXPORT
    # ----------------------------------------------------------------------
    def enable_export(self, state):
        self.export_btn.setEnabled(state)


    # ----------------------------------------------------------------------
    # helper functions
    # ----------------------------------------------------------------------
    # handles key events for navigating left and right between lists
    def keyPressEvent(self, event):
        print('key pressed')
        key = event.key()

        if key == QtCore.Qt.Key_Right:
            # if typesList has focus
            if self.typesList.tbaList.hasFocus():
                # select last version
                print('keyPressEvent, select version')
                num = self.versionList.tbaList.count()
                if num == 0 or self.versionAutoVersion.isChecked():
                    return
                item = self.versionList.tbaList.item(num-1)
                self.versionList.tbaList.setCurrentItem(item)
                self.selVersion = item.text()
                self.versionList.tbaList.setFocus()
            elif self.assetList.tbaList.hasFocus():
                # select first selectable type
                print('keyPressEvent, select type')
                for i in range(self.typesList.tbaList.count()):
                    if self.typesList.tbaList.item(i).flags() & QtCore.Qt.ItemIsSelectable:
                        self.typesList.tbaList.setCurrentRow(i)
                        self.typesList.tbaList.setFocus()
                        return
            else:
                # select first selectable asset
                print('keyPressEvent, select asset')
                for i in range(self.assetList.tbaList.count()):
                    if self.assetList.tbaList.item(i).flags() & QtCore.Qt.ItemIsSelectable:
                        self.assetList.tbaList.setCurrentRow(i)
                        self.assetList.tbaList.setFocus()
                        return
        elif key == QtCore.Qt.Key_Left:
            if self.versionList.tbaList.hasFocus():
                print('keyPressEvent, select type')
                self.typesList.tbaList.setFocus()
                self.selVersion = None
                self.updateVersionList()
            elif self.typesList.tbaList.hasFocus():
                print('keyPressEvent, select asset')
                self.assetList.tbaList.setFocus()
                self.selType = None
                # deselect all
                self.typesList.tbaList.setCurrentRow(-1)
                self.updateTypeList()
        elif key == QtCore.Qt.Key_Escape:
            self.close()

    def deleteAsset(self):
        print('deleteAsset')
        path = self.getAssetPath()

        res = QtWidgets.QMessageBox.question(self, "You are about to delete an asset on disk!", "Are you sure?",
                                QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)

        if res == QtWidgets.QMessageBox.Ok:
            print('Deleting: {0}'.format(path))

            try:
                shutil.rmtree(path)
            except OSError as e:
                print ("Error: %s - %s." % (e.path, e.strerror))
            else:
                print('Successfully deleted: {0}'.format(path))
                self.updateAssetList()

    def exploreFile(self, which):
        path = self.getAssetPath()

        if not path:
            print('Could not build asset path')
            return

        if self.PLATFORM == "win32":
            print('Explore file in windows explorer')
            subprocess.Popen(r'explorer /select, ' + path)
        elif self.PLATFORM == "darwin":
            print('Explore file in max finder')
            subprocess.Popen(["open", path])
        else:
            print('OS is linux, ignoring..')

    def enableItem(self, item):
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        item.setTextColor(QtGui.QColor('white'))

    def disableItem(self, item):
        item.setFlags(QtCore.Qt.NoItemFlags)

    def darkenItem(self, item):
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        item.setTextColor(self.DARK_COLOUR)

    def italicItem(self, item):
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        font = item.font()
        font.setItalic(True)
        item.setFont(font)

    def camelCase(self, st):
        if not st.strip():
            return st

        output = ''.join(x for x in st.title() if x.isalnum())
        return output[0].lower() + output[1:]

    # ----------------------------------------------------------------------
    # EXPORT FUNCTIONS
    # ----------------------------------------------------------------------

    def export(self):
        print('EXPORT')
        exportVersion = self.versionList.footer.text()

        if not self.selAsset:
            print('No asset specified')
            return
        elif not self.selType:
            print('No asset type specified')
            return
        elif not exportVersion:
            print('No version specified')
            return

        print('EXPORT VARIABLES')
        print('EXPORT DIR: {0}'.format(self.exportDir))
        print('PUBLISH DIR: {0}'.format(self.publishDir))
        print('SEL ASSET: {0}'.format(self.selAsset))
        print('SEL TYPE: {0}'.format(self.selType))
        print('EXPORT VERSION: {0}'.format(exportVersion))

        assetExportDir = os.path.join(self.exportDir, 'assets', self.selAsset, self.selType, exportVersion)
        assetPublishDir = os.path.join(self.publishDir, 'assets', self.selAsset, self.selType, exportVersion)

        msg = ''
        msg2 = 'Create it?'
        missingDirs = []

        if not os.path.exists(self.exportDir) and not not os.path.exists(self.publishDir):
            msg = "Neither 'exports' or '_published3d' directory exists"
            msg2 = 'Create both?'
            missingDirs = [self.exportDir, self.publishDir]
        elif not os.path.exists(self.exportDir):
            msg = "'exports' folder does not exist"
            missingDirs = [self.exportDir]
        elif not os.path.exists(self.publishDir):
            msg = "'_published3d' folder does not exist"
            missingDirs = [self.publishDir]

        # if either directory doesn't exist, ask if user wants to create it
        if len(missingDirs) > 0:
            msgBox = QtWidgets.QMessageBox(self)
            msgBox.setText( msg )
            msgBox.setInformativeText( msg2 )
            msgBox.setStandardButtons( QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel )
            msgBox.setDefaultButton( QtWidgets.QMessageBox.Ok )

            res = msgBox.exec_()

            if res == QtWidgets.QMessageBox.Ok:
                for missingDir in missingDirs:
                    print('Creating directories: {0}'.format(missingDir))
                    os.makedirs(missingDir)
            else:
                print('Not creating directories. Exiting')
                return

        # EXPORT
        exportResults = []
        exportResults.append(assetExportDir)

        self.exportAssetJsonFile(assetExportDir, exportVersion)

        if self.publish_cb.isChecked():
            exportResults.append(assetPublishDir)

            self.exportAssetJsonFile(assetPublishDir, exportVersion)

        print('\n\n\nEXPORT RESULTS')
        print(exportResults)

        results_dialog = TBAExportResultsDialog(exportResults)

        result = results_dialog.exec_()

    def exportAssetJsonFile(self, exportDir, assetVersion, dryRun=False):
        print('exportAssetJsonFile')

        assetName = self.selAsset
        assetType = self.selType

        print('ASSET NAME')
        print(assetName)
        print('ASSET TYPE')
        print(assetType)
        print('ASSET VERSION')
        print(assetVersion)

        filepath = assetName + '_' + assetType + '.json'

        scene = 'EXAMPLE SCENE PATH'

        # make export path for json file
        jsonPath = os.path.join(exportDir, filepath)

        if dryRun:
            print('Asset json export path is: {0}'.format(jsonPath))
            return

        # get notes
        notes = self.notes.toPlainText()

        # build json data
        data = {}

        data['assetName'] = assetName
        data['assetType'] = assetType
        data['assetVersion'] = assetVersion
        data['notes'] = notes
        data['scene'] = scene
        data['user'] = getpass.getuser()

        dataObjs = []

        data['objects'] = dataObjs

        # ensure directory exists
        if not os.path.exists(exportDir):
            os.makedirs(exportDir)

        # write json file
        with open(jsonPath, 'w') as outfile:
            json.dump(data, outfile, indent=4, sort_keys=True)

        print('Created a hidden json file here: {0}'.format(outfile))

        # make file hidden
        # subprocess.check_call(["attrib","+H",jsonPath])

        self.updateAssetList()

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

    my_dialog = TBAAssetExporter(maya_main_window())
    my_dialog.show()


def run_standalone():
    print('TBA :: Run Standalone')
    app = QtWidgets.QApplication(sys.argv)

    module_path = os.path.dirname(os.path.abspath(__file__))

    app.setStyleSheet(sqss_compiler.compile(
        os.path.join(module_path,'TBA_stylesheet.scss'),
        os.path.join(module_path,'variables.scss'),
    ))

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


