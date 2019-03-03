import sys
import os
import getpass

from PySide2 import QtCore, QtWidgets, QtGui

sys.dont_write_bytecode = True  # Avoid writing .pyc files

import sqss_compiler
import TBA_UI

import TBA_IO_resources

import tba_maya_api
import TBA_IO_chips
#import maya.cmds as mc

class TBA_IO_collection_list(QtWidgets.QDialog):
    importer = False
    cbIds = []

    app = None

    assets = {}

    stage = ''
    entity = ''

    selected = None

    TASKS = ['model','layout','rig','anim','fx','light']

    def __init__(self, parent=None, app=None):
        super(TBA_IO_collection_list, self).__init__(parent)
        self.app = app

        # unique object name for maya
        self.setObjectName('TBA_IO_collection_list')

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        # self.setMinimumWidth(200)
        self.setGeometry(100,100,400,200)

        self.update_workspace()

        #self.refresh()

    def create_widgets(self):
        self.header = QtWidgets.QLabel('Collections')
        self.header.setAlignment(QtCore.Qt.AlignTop)

        self.list = QtWidgets.QListWidget()

        self.add_btn = QtWidgets.QPushButton('+')
        self.add_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.add_btn.setStyleSheet('font-size: 20px; width:22px; height:22px; margin:0; padding:0 0 4 1;')

        self.assetName = QtWidgets.QLabel('Name') 
        self.assetStage = QtWidgets.QLabel('Stage')
        self.assetEntity = QtWidgets.QLabel('Entity')
        self.assetTask = QtWidgets.QLabel('Task')
        self.assetTask.hide()
        self.assetTaskCombo = QtWidgets.QComboBox()
        # self.assetTaskCombo.setStyleSheet('background-color:rgb(80,85,90); color:#ccc;')
        self.assetTaskCombo.addItems(self.TASKS)
        self.assetVersion = QtWidgets.QLabel()
        self.author = QtWidgets.QLabel()
        self.dateUpdated = QtWidgets.QLabel()

        self.chips = TBA_IO_chips.ChipsAutocomplete()
        self.chips.addItems(['apple', 'lemon', 'orange', 'mango', 'papaya', 'strawberry'])

    def create_layouts(self):
        # self must be passed to the main_layout so it is parented to the dialog instance
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)

        #### LEFT ####
        left_frame = QtWidgets.QFrame()
        left_frame.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        left_frame.setMinimumWidth(200)

        left_layout = QtWidgets.QVBoxLayout(left_frame)
        left_layout.setSpacing(0)
        left_layout.setContentsMargins(0,0,0,0)

        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setContentsMargins(0,0,0,0)

        header_layout.addWidget(QtWidgets.QLabel('Collections'))
        header_layout.addStretch()
        header_layout.addWidget(self.add_btn)

        left_layout.addLayout(header_layout)
        left_layout.addWidget(self.list)

        #### RIGHT ####

        right_frame = QtWidgets.QFrame()
        right_frame.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        right_frame.setMinimumWidth(200)

        right_layout = QtWidgets.QVBoxLayout(right_frame)
        right_layout.setContentsMargins(0,0,0,0)
        right_layout.setAlignment(QtCore.Qt.AlignTop)

        # form_layout = QtWidgets.QFormLayout()
        # form_layout.setFormAlignment(QtCore.Qt.AlignLeft)
        # form_layout.setLabelAlignment(QtCore.Qt.AlignLeft)
        # form_layout.addRow('Name', self.assetName)
        # form_layout.addRow('Task', self.assetTask)
        # form_layout.addRow('Author', QtWidgets.QLabel('Mike Battcock'))

        header_properties = QtWidgets.QLabel('Properties')
        header_properties.setContentsMargins(0,5,0,0)

        right_layout.addWidget(header_properties)

        self.properties_frame = QtWidgets.QFrame()
        self.properties_frame.hide()

        properties_layout = QtWidgets.QVBoxLayout()
        self.properties_frame.setLayout(properties_layout)
        
        properties_layout.addWidget(self.assetName)
        properties_layout.addWidget(self.assetStage)
        properties_layout.addWidget(self.assetEntity)
        properties_layout.addWidget(self.assetTaskCombo)
        properties_layout.addWidget(self.assetTask)

        properties_layout.addWidget(self.chips)

        right_layout.addWidget(self.properties_frame)

        # right_layout.addLayout(form_layout)

        main_layout.addWidget(left_frame)
        main_layout.addWidget(right_frame)

    def create_connections(self):
        if (self.app == 'maya'):
            self.add_btn.clicked.connect(self.add_item_maya)
        else:
            self.add_btn.clicked.connect(self.add_item_standalone)

        self.list.itemChanged.connect(self.list_item_edited)
        self.list.itemClicked.connect(self.list_item_clicked)

        self.chips.updated.connect(self.chips_updated)

    def list_item_edited(self, item):
        print('list_item_edited')

        text = item.text().strip()

        if text:
            self.create_properties(item)

        self.selected = item.text()

    def list_item_clicked(self, item):
        if self.selected == item.text():
            return
            
        print('list_item_clicked')
        asset = item.data(QtCore.Qt.UserRole)
        
        self.update_properties(item)
        self.chips.update_chips(asset['tags'])

        self.selected = item.text()

    def refresh(self):
        print('TBA_IO_collection_list - refresh_list')

        #cbIds.extend(tba_maya_api.set_asset_callbacks())

        tba_assets = tba_maya_api.get_maya_assets()

        self.list.clear()

        for name in tba_assets:
            item = QtWidgets.QListWidgetItem(name, self.list)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEditable)
            item.setCheckState(QtCore.Qt.Checked)

    def create_properties(self, item):
        asset_name = item.text()
        print('create_properties')

        asset = {
            'assetName': asset_name,
            'assetTask': 'model',
            'assetStage': self.stage,
            'assetEntity': self.entity,
            'tags': [],
            'author': getpass.getuser(),
        }

        item.setData(QtCore.Qt.UserRole, asset)

        self.update_properties(item)

    def update_properties(self, item):
        asset = item.data(QtCore.Qt.UserRole)
        print('update_properties, item: {0}, asset: {1}'.format(item.text(), asset))
        
        self.properties_frame.show()

        self.assetName.setText(asset['assetName'])
        self.assetStage.setText(asset['assetStage'])
        self.assetEntity.setText(asset['assetEntity'])

        # self.chips.update_chips(asset['tags'])

    def chips_updated(self, chips):
        print('chips_updated')
        print(chips)

        item = self.list.currentItem()

        asset = item.data(QtCore.Qt.UserRole)
        asset['tags'] =  chips

        item.setData(QtCore.Qt.UserRole, asset)

        print('CHIPS_UPDATED, item: {0}, asset: {1}'.format(item.text(), asset))

    def add_item_maya(self):
        # sel = tba_maya_api.get_selection()

        # for obj in sel:
        #     assetName = obj.split('|')[-1]
        #     assetName = assetName.lower().split('grp')[0].rstrip('_')

        #     if assetName in self.assets:
        #         continue

        #     item = QtWidgets.QListWidgetItem(assetName)
        #     item.setBackground(QtGui.QColor(80,85,90,150))
        #     item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEditable)
        #     item.setCheckState(QtCore.Qt.Checked)
        #     item.setSelected(True)
            
        #     self.list.addItem(item)
        #     self.create_properties(assetName)
        #     # self.list.editItem(item)

        # return



        tba_sets = tba_maya_api.create_tba_sets()

        for tba_set in tba_sets:
            asset = {
                'assetName': tba_set,
                'assetTask': 'model',
                'assetStage': self.stage,
                'assetEntity': self.entity,
                'tags':[],
                'author': getpass.getuser(),
            }

            item = QtWidgets.QListWidgetItem(tba_set)
            item.setData(QtCore.Qt.UserRole, asset)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEditable)
            item.setCheckState(QtCore.Qt.Checked)
            self.list.addItem(item)

    def add_item_standalone(self):
        item = QtWidgets.QListWidgetItem('')
        item.setBackground(QtGui.QColor(80,85,90,150))
        item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEditable)
        item.setCheckState(QtCore.Qt.Checked)
        item.setSelected(True)
        self.list.addItem(item)

        self.list.editItem(item)

    def update_workspace(self):
        if self.app == 'maya':
            scene = tba_maya_api.get_scene_path()
        else:
            scene = '/Users/michaelbattcock/Documents/VFX/TBA/0907TBA_1018_RnD/vfx/build/shapes/maya/scenes/shapes_mlb_v001.mb'

        parts = scene.split(os.sep)

        if not 'vfx' in parts:
            print('vfx not found in scene path')
            return

        vfxIdx = parts.index('vfx')

        self.stage = parts[vfxIdx + 1]
        self.entity = parts[vfxIdx + 2]

    def mousePressEvent(self, event):
        print('mouse press event')
        self.chips.hide_list()
        self.chips.input.clearFocus()

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
