import sys
import os
import platform
import re
import json
import subprocess
import getpass

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

class TBAAssetExporter(QtWidgets.QDialog):
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

        self.range_start_le = QtWidgets.QLineEdit()
        self.range_end_le = QtWidgets.QLineEdit()        

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

        self.typesList.tbaList.itemSelectionChanged.connect(self.onTypeSelected)
        self.typesCombo.currentIndexChanged.connect(self.onTypeComboSelected)

        self.versionList.tbaList.itemSelectionChanged.connect(self.onVersionSelected)
        self.versionAutoVersion.stateChanged.connect(self.onAutoVersionChanged)

        self.export_btn.clicked.connect(self.export)

    def getExportDir(self):
        # this function would look up the _published3d directory relative to the scene
        if MAYA:
            currentDir = mc.workspace(q=1,fullName=1)
        else:
            currentDir = os.path.dirname(os.path.realpath(__file__))

        #publishDir = os.path.join(currentDir, '_published3d')
        self.exportDir = os.path.join(currentDir, self.exportDirName)
        self.publishDir = os.path.join(currentDir, '..', self.publishDirName)     


    # ----------------------------------------------------------------------
    # ASSET LIST LOGIC
    # ----------------------------------------------------------------------
    def updateTempAssetName(self,name):
        print('updateTempAssetName: {0}'.format(name))

        if len(name) == 0:
            print('updateTempAssetName: removeTempAsset')
            self.removeTempAsset()
            return
        else:
            self.selAsset = name
            items = self.assetList.tbaList.findItems(name, QtCore.Qt.MatchExactly)

            if items:
                self.removeTempAsset()

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
                #self.assetList.tbaList.setCurrentRow(i-1)
                #item = self.assetList.tbaList.takeItem(i)
                #item = None

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
            print('onAssetSelected: set selAsset to {0}'.format(self.selAsset))
            self.selAsset = item.text()

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

        if not os.path.exists(exportedAssetsDir):
            print('Assets exports directory does not exist: {0}'.format(exportedAssetsDir))
            return

        if not os.path.exists(publishedAssetsDir):
            print('Assets _published3d directory does not exist: {0}'.format(publishedAssetsDir))
            return

        exportedAssets = sorted(os.listdir(exportedAssetsDir))
        publishedAssetsDir = sorted(os.listdir(publishedAssetsDir))

        # add assets to asset list
        for asset in exportedAssets:
            # ignore hidden files
            if asset.startswith('.'):
                continue

            item = QtWidgets.QListWidgetItem(asset)

            if asset == selAsset:
                item.setSelected(True)

            self.assetList.tbaList.addItem(item)

            if asset not in publishedAssetsDir:
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
        print item

        if item:
            self.selType = item.text() 
        
        self.updateVersionList()
        self.updateFormatList()

        # select type in combobox
        index = self.typesCombo.findText(self.selType, QtCore.Qt.MatchFixedString)
        if index >= 0:
             self.typesCombo.setCurrentIndex(index)

    def onTypeComboSelected(self, idx):
        print 'type combo selected'

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
        print 'updateVersionList'

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

    def onAutoVersionChanged(self):
        if self.versionAutoVersion.isChecked():
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
                    print 'couldnt extract version number'
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
        print 'updateFormatList'
        self.formatsCombo.clear()

        formats = self.FORMATS[self.selType]
 
        self.formatsCombo.addItems(formats)

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
            # if 'active' list is selType select last version
            if self.selType:
                # select last version
                print('keyPressEvent, select version')
                num = self.versionList.tbaList.count()
                if num == 0 or self.versionAutoVersion.isChecked():
                    return
                item = self.versionList.tbaList.item(num-1)
                self.versionList.tbaList.setCurrentItem(item)
                self.selVersion = item.text()
                self.versionList.tbaList.setFocus()
            elif self.selAsset:
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
            if self.selVersion:
                print('keyPressEvent, select type')
                self.typesList.tbaList.setFocus()
                self.selVersion = None
                self.updateVersionList()
            elif self.selType:
                print('keyPressEvent, select asset')
                self.assetList.tbaList.setFocus()
                self.selType = None
                # deselect all
                self.typesList.tbaList.setCurrentRow(-1)
                self.updateTypeList()

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


    # ----------------------------------------------------------------------
    # EXPORT FUNCTIONS
    # ----------------------------------------------------------------------
    
    def export(self):
        print 'EXPORT'
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

        exportDir = os.path.join(self.exportDir, 'assets', self.selAsset, self.selType, exportVersion)

        self.exportAssetJsonFile(exportDir, exportVersion)

        if self.publish_cb.isChecked():
            exportDir = os.path.join(self.publishDir, 'assets', self.selAsset, self.selType, exportVersion)
            self.exportAssetJsonFile(exportDir, exportVersion)

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
            print 'Asset json export path is ' + jsonPath
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

        print 'Created a hidden json file here:'
        print outfile

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
    app.setStyleSheet(sqss_compiler.compile('TBA_stylesheet.scss', 'variables.scss'))
    # app.setStyleSheet('TBA_stylesheet.scss')
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


