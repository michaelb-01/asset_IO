import sys
import os
import getpass
import datetime

from PySide2 import QtCore, QtWidgets, QtGui

import TBA_IO_chips
try:
    import tba_utils_maya
except:
    print('Not in maya')

import TBA_IO_resources

import sqss_compiler

sys.dont_write_bytecode = True  # Avoid writing .pyc files

class TBA_IO_collection_list(QtWidgets.QDialog):
    importer = False
    cbIds = []

    app = None

    assets = {}

    stage = ''
    entity = ''
    task = ''

    count = 0
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
        self.setGeometry(100,100,400,160)

        self.update_workspace()

        if self.app == 'maya':
            self.refresh()

    def create_widgets(self):
        self.header_collections = QtWidgets.QLabel('Collections')
        # self.header_collections.setStyleSheet('font-size: 14px;')

        self.header_properties = QtWidgets.QLabel('Properties')
        self.header_properties.setContentsMargins(0,6,0,0)
        # self.header_properties.setStyleSheet('font-size: 14px;')

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
        self.assetTaskCombo.setStyleSheet('border: none;')
        self.assetTaskCombo.addItems(self.TASKS)
        self.assetVersion = QtWidgets.QLabel()
        self.author = QtWidgets.QLabel()
        self.dateUpdated = QtWidgets.QLabel()

        self.chips = TBA_IO_chips.ChipsAutocomplete()
        self.chips.addItems(['apple', 'lemon', 'orange', 'mango', 'papaya', 'strawberry'])

        self.test = QtWidgets.QPushButton('test')

    def create_layouts(self):
        # self must be passed to the main_layout so it is parented to the dialog instance
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setSpacing(10)
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

        header_layout.addWidget(self.header_collections)
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

        right_layout.addWidget(self.header_properties)

        self.properties_frame = QtWidgets.QFrame()
        self.properties_frame.setFrameStyle(QtWidgets.QFrame.StyledPanel);
        self.properties_frame.hide()

        self.properties_layout = QtWidgets.QVBoxLayout()
        self.properties_frame.setLayout(self.properties_layout)

        form_layout = QtWidgets.QFormLayout()

        form_layout.setLabelAlignment(QtCore.Qt.AlignLeft)
        form_layout.setFormAlignment(QtCore.Qt.AlignLeft)


        form_layout.addRow('Name:', self.assetName)
        form_layout.addRow('Stage:', self.assetStage)
        form_layout.addRow('Entity:', self.assetEntity)

        form_layout.addRow('Task:', self.assetTaskCombo)

        self.properties_layout.addLayout(form_layout)
        self.properties_layout.addWidget(self.chips)

        right_layout.addWidget(self.properties_frame)

        # right_layout.addLayout(form_layout)

        main_layout.addWidget(left_frame)
        main_layout.addWidget(right_frame)
        # main_layout.addWidget(self.test)

    def create_connections(self):
        if (self.app == 'maya'):
            self.add_btn.clicked.connect(self.add_item_maya)
        else:
            self.add_btn.clicked.connect(self.add_item_standalone)

        self.list.itemChanged.connect(self.list_item_edited)
        self.list.itemClicked.connect(self.list_item_clicked)

        self.chips.updated.connect(self.chips_updated)

        self.assetTaskCombo.currentIndexChanged.connect(self.task_changed)
        self.test.clicked.connect(self.solidify_task)

    def solidify_task(self):
        print('solidify task')
        self.assetTaskCombo.deleteLater()
        self.properties_layout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.assetTask)

    def list_item_edited(self, item):
        print('list_item_edited, count: {0}, list.count: {1}, selected: {2}'.format(self.count, self.list.count(), self.selected))

        text = item.text().strip()

        # remove item if empty name
        if not text:
            self.list.takeItem(item)
            return
        if text == self.selected:
            return

        self.selected = text

        # update asset name
        asset = item.data(QtCore.Qt.UserRole)
        if asset['name'] != text:
            asset['name'] = text
            item.setData(QtCore.Qt.UserRole, asset)

        self.update_properties(item)

    def list_item_clicked(self, item):
        print('list_item_clicked')

        # ignore if already selected
        if self.selected == item.text():
            print('item already selected, ignoring')
            return

        asset = item.data(QtCore.Qt.UserRole)

        self.update_properties(item)
        self.chips.update_chips(asset['tags'])

        self.selected = item.text()

    def refresh(self):
        print('TBA_IO_collection_list - refresh_list')

        #cbIds.extend(tba_maya_api.set_asset_callbacks())

        tba_assets = tba_utils_maya.get_tba_assets()

        self.list.clear()

        for asset in tba_assets:
            print('asset is: ')
            print(asset)
            item = QtWidgets.QListWidgetItem(asset['name'], self.list)
            item.setData(QtCore.Qt.UserRole, asset)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEditable)
            item.setCheckState(QtCore.Qt.Checked)

    def create_properties(self, item):
        asset_name = item.text()
        print('create_properties')
        return

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

        self.assetName.setText(asset['name'])
        self.assetStage.setText(asset['stage'])
        self.assetEntity.setText(asset['entity'])

        taskIndex = self.TASKS.index(asset['type'])
        self.assetTaskCombo.setCurrentIndex(taskIndex)

        # self.chips.update_chips(asset['tags'])

    def task_changed(self, index):
        print('task_changed, index: {0}'.format(index))
        item = self.list.currentItem()

        asset = item.data(QtCore.Qt.UserRole)
        asset['type'] = self.TASKS[index]

        item.setData(QtCore.Qt.UserRole, asset)

    def chips_updated(self, chips):
        print('chips_updated, chips: {0}'.format(chips))
        print(chips)

        item = self.list.currentItem()

        asset = item.data(QtCore.Qt.UserRole)
        asset['tags'] =  chips

        item.setData(QtCore.Qt.UserRole, asset)

    def add_item_maya(self):
        # create maya sets from selected objects
        # assets = tba_utils_maya.prep_tba_assets()
        assets = tba_utils_maya.create_tba_assets()

        for asset in assets:
            # create list widget item
            item = QtWidgets.QListWidgetItem(asset['name'])
            # colour item to show it has not yet been exported
            item.setBackground(QtGui.QColor(80,85,90,150))
            # store asset data as user data on item
            item.setData(QtCore.Qt.UserRole, asset)
            # make checkable, checked and editable
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEditable)
            item.setCheckState(QtCore.Qt.Checked)
            self.list.addItem(item)

    def add_item_standalone(self):
        asset = {
            'name': '',
            'type': 'model',
            'stage': self.stage,
            'entity': self.entity,
            'tags':[],
            'author': getpass.getuser(),
        }

        # create list widget item
        item = QtWidgets.QListWidgetItem('')
        # colour item to show it has not yet been exported
        item.setBackground(QtGui.QColor(80,85,90,150))
        # store asset data as user data on item
        item.setData(QtCore.Qt.UserRole, asset)
        # make checkable, checked and editable
        item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEditable)
        item.setCheckState(QtCore.Qt.Checked)
        self.list.addItem(item)

        self.list.editItem(item)

    def update_workspace(self):
        if self.app == 'maya':
            scene = tba_utils_maya.get_scene_path()
        else:
            scene = os.path.abspath('/Users/michaelbattcock/Documents/VFX/TBA/0907TBA_1018_RnD/vfx/build/shapes/maya/scenes/shapes_mlb_v001.mb')

        parts = scene.split(os.sep)

        if not 'vfx' in parts:
            print('vfx not found in scene {0}'.format(parts))
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
