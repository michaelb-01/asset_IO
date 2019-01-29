import sys
import os

from PySide2 import QtCore, QtWidgets, QtGui

sys.dont_write_bytecode = True  # Avoid writing .pyc files

import sqss_compiler
import TBA_UI

class TBA_IO_asset_list(QtWidgets.QDialog):
    importer = False

    # tasks and their associated formats
    TASKS = {
        'camera':['abc','fbx','mb'],
        'model':['abc','obj','fbx','mb'],
        'anim':['abc','fbx','mb'],
        'fx':['abc','mb'],
        'rig':['mb'],
        'light':['mb']
    }

    work_root = None

    stage = 'build'
    entity = ''

    # export and publish dirs
    export_dir = None
    publish_dir = None

    DARK_COLOUR = QtGui.QColor(80,85,95)

    def __init__(self, parent=None):
        super(TBA_IO_asset_list, self).__init__(parent)

        # unique object name for maya
        self.setObjectName('MyLabel')

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.header_label = QtWidgets.QLabel('Asset Browser')
        self.header_label.setObjectName('h2')

        self.home_icon = QtGui.QPixmap('icons/home_white.png')
        self.home_btn = QtWidgets.QPushButton('')
        self.home_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.home_btn.setIcon(self.home_icon)

        self.right_icon = QtGui.QPixmap('icons/arrow_right_white.png')
        self.right_btn = QtWidgets.QPushButton('')
        self.right_btn.setDisabled(True)
        self.right_btn.setIcon(self.right_icon)

        self.right_icon2 = QtGui.QPixmap('icons/arrow_right_white.png')
        self.right_btn2 = QtWidgets.QPushButton('')
        self.right_btn2.setIcon(self.right_icon2)

        self.stage_btn = QtWidgets.QPushButton('build')
        self.stage_btn.setFixedWidth(50)
        self.stage_btn.setCursor(QtCore.Qt.PointingHandCursor)

        self.stage_menu = QtWidgets.QMenu(self)
        self.stage_menu.setCursor(QtCore.Qt.PointingHandCursor)
        self.stage_menu.addAction('build', lambda: self.setStage('build'))
        self.stage_menu.addAction('shots', lambda: self.setStage('shots'))

        self.stage_btn.setMenu(self.stage_menu)

        self.entity_btn = QtWidgets.QPushButton('')
        self.entity_btn.setCursor(QtCore.Qt.PointingHandCursor)

        self.refresh_btn = QtWidgets.QPushButton('')
        self.refresh_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.refresh_icon = QtGui.QPixmap('icons/refresh_white.png')
        self.refresh_btn.setIcon(self.refresh_icon)

        self.asset_list_label = QtWidgets.QLabel('Assets')
        self.asset_list = TBA_UI.TBA_list_draggable()

        self.types_list_label = QtWidgets.QLabel('Tasks')
        self.types_list = TBA_UI.TBA_list_draggable()

        for task in self.TASKS:
            item = QtWidgets.QListWidgetItem(task)
            self.disableItem(item)
            self.types_list.addItem(item)

    def create_layouts(self):
        # self must be passed to the main_layout so it is parented to the dialog instance
        main_layout = QtWidgets.QVBoxLayout(self)

        # header layout for title and refresh btn
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.addWidget(self.header_label)
        header_layout.addWidget(self.home_btn)
        header_layout.addWidget(self.right_btn)
        header_layout.addWidget(self.stage_btn)
        header_layout.addWidget(self.right_btn2)
        header_layout.addWidget(self.entity_btn)
        header_layout.addStretch()
        header_layout.addWidget(self.refresh_btn)

        # horizontal layout to hold asset and types list
        lists_layout = QtWidgets.QHBoxLayout()

        # asset list layout
        asset_list_layout = QtWidgets.QVBoxLayout()
        asset_list_layout.addWidget(self.asset_list_label)
        asset_list_layout.addWidget(self.asset_list)

        # types list layout
        types_list_layout = QtWidgets.QVBoxLayout()
        types_list_layout.addWidget(self.types_list_label)
        types_list_layout.addWidget(self.types_list)

        # add asset and types lists to lists layout
        lists_layout.addLayout(asset_list_layout)
        lists_layout.addLayout(types_list_layout)

        main_layout.addLayout(header_layout)
        main_layout.addLayout(lists_layout)

    def create_connections(self):
        self.refresh_btn.clicked.connect(self.update_asset_list)

        #self.work_area.clicked.connect(self.get_work_area)
        #self.stage_btn.clicked.connect(self.on_stage_clicked)

        self.asset_list.itemSelectionChanged.connect(self.on_asset_selected)
        self.asset_list.rightClicked.connect(self.asset_right_clicked)

        self.entity_btn.clicked.connect(self.update_entity_menu)

        #self.types_list.itemSelectionChanged.connect(self.on_typ)
        self.types_list.rightClicked.connect(self.asset_right_clicked)

    def update_exports_dirs(self, export_dir=None, publish_dir=None):
        print('TBA :: update_exports_dirs')

        print('Export directory: {0}'.format(export_dir))
        print('Publish directory: {0}'.format(publish_dir))

        self.export_dir = export_dir
        self.publish_dir = publish_dir

        # update asset list
        self.update_asset_list()

    def set_root(self, root):
        print('Setting work root to: {0}'.format(root))
        self.work_root = root

        self.get_work_areas()

    def setStage(self, stage):
        print('select stage: {0}'.format(stage))



        if stage != self.stage:
            self.stage_btn.setText(stage)

    def setEntity(self, entity):
        print('select entity: {0}'.format(entity))

        self.entity_btn.setText(entity)

        # remove menu
        self.entity_menu = None

    def update_entity_menu(self):
        print('update entity menu')

        if not self.work_root:
            print('Couldnt find work root')
            return

        self.entity_menu = QtWidgets.QMenu(self)
        self.entity_menu.setCursor(QtCore.Qt.PointingHandCursor)

        entities_dir = os.path.join(self.work_root, self.stage_btn.text())

        entities = []

        if os.path.exists(entities_dir):
            entities = os.listdir(entities_dir)

        # populate menu
        for entity in entities:
            self.entity_menu.addAction(entity, lambda entity=entity: self.setEntity(entity))

        self.entity_btn.setMenu(self.entity_menu)
        self.entity_btn.showMenu()

    def get_work_areas(self):
        print('get work area')
        if not self.work_root:
            print('Couldnt find work root')
            return

        build_dir = os.path.join(self.work_root, 'build')
        shots_dir = os.path.join(self.work_root, 'shots')

        build_entities = []

        if os.path.exists(build_dir):
            build_entities = os.listdir(build_dir)

        if os.path.exists(shots_dir):
            shots = os.listdir(shots_dir)

        print('build entities: {0}'.format(build_entities))
        print('shots: {0}'.format(shots))

    def update_asset_list(self):
        print('TBA :: update_asset_list')

        # store current item for selection after list is rebuilt
        sel_asset = self.asset_list.currentItem()

        if sel_asset:
            print('set sel_asset to its text')
            sel_asset = sel_asset.text()

        # clear all items, will repopulate later in this function
        self.asset_list.clear()

        # exported and published assets
        exportedAssets = []
        publishedAssets = []

        # check directories exist then get assets
        if os.path.exists(self.export_dir):
            exportedAssets = sorted(os.listdir(self.export_dir))
        else:
            print('Assets exports directory does not exist: {0}'.format(self.export_dir))

        if os.path.exists(self.publish_dir):
            publishedAssets = sorted(os.listdir(self.publish_dir))
        else:
            print('Assets _published3d directory does not exist: {0}'.format(self.publish_dir))

        # add assets to asset list
        for asset in exportedAssets:
            # ignore hidden files
            if asset.startswith('.'):
                continue

            # new list item
            item = QtWidgets.QListWidgetItem(asset)

            # reselect item if it was previously selected
            if asset == sel_asset:
                item.setSelected(True)

            # add item
            self.asset_list.addItem(item)

            # italicize if asset is only in exports and not published
            if asset not in publishedAssets:
                self.italicItem(item)

            # reselect item if it was selected
            if asset == sel_asset:
                self.asset_list.setCurrentItem(item)

            # set focus

    def on_asset_selected(self):
        print('TBA :: on_asset_selected')
        item = self.asset_list.currentItem()

        # if user deselected the item
        if not self.asset_list.selectedItems():
            print('on_asset_selected: set sel_asset to None')
            self.sel_asset = None
        else:
            self.sel_asset = item.text()
            print('on_asset_selected: set sel_asset to {0}'.format(self.sel_asset))

        # update type list
        self.updateTypeList()
        self.select_enabled_type()

    def updateTypeList(self):
        print('TBA :: updateTypeList')

        if not self.sel_asset:
            print('updateTypeList, disableAllTypes')
            self.disableAllTypes()
            return

        # exported assets directory
        exported_asset_dir = os.path.join(self.export_dir, self.sel_asset)
        # published assets directory
        published_asset_dir = os.path.join(self.publish_dir, self.sel_asset)

        # exported and published types
        exported_types = []
        published_assets = []

        # list folders inside exports dir
        if os.path.exists(exported_asset_dir):
            exported_types = sorted(os.listdir(exported_asset_dir))
        else:
            print('Asset export directory does not exist: {0}'.format(exported_asset_dir))

        if os.path.exists(published_asset_dir):
            published_assets = sorted(os.listdir(published_asset_dir))
        else:
            print('Asset publish directory does not exist: {0}'.format(published_asset_dir))

        # iterate over types and disable if not found
        for i in range(self.types_list.count()):
            item = self.types_list.item(i)

            # if we are in the importer set the selectability of the item
            # else just change the colour to illustrate what has already been exported
            if item.text() in exported_types:
                self.enableItem(item)
                if item.text() not in published_assets:
                    self.italicItem(item)
            else:
                if self.importer:
                    self.disableItem(item)
                else:
                    self.darkenItem(item)

    def onSelectionUpdate(self):
        print('TBA :: onSelectionUpdate')

    def asset_right_clicked(self, pos):
        print('TBA :: asset_right_clicked')

        contextMenu = QtWidgets.QMenu(self)
        contextMenu.setCursor(QtCore.Qt.PointingHandCursor)

        deleteAct = contextMenu.addAction('Delete')
        exploreAct = contextMenu.addAction('Explore')

        action = contextMenu.exec_(pos)

        if action == deleteAct:
            self.deleteAsset()
        elif action == exploreAct:
            print('explore asset')
            self.exploreFile(0)

    def select_enabled_type(self):
        print('TBA :: select_enabled_type')
        for i in range(self.types_list.count()):
            if self.types_list.item(i).flags() & QtCore.Qt.ItemIsSelectable:
                if self.types_list.item(i).textColor() == QtGui.QColor('white'):
                    self.types_list.item(i).setSelected(True)
                    self.types_list.setCurrentRow(i)
                    self.types_list.setFocus()
                    return

    def select_enabled_asset(self):
        print('TBA :: select_enabled_asset')
        for i in range(self.asset_list.count()):
            if self.asset_list.item(i).flags() & QtCore.Qt.ItemIsSelectable:
                print('select item: {0}'.format(self.asset_list.item(i)))
                self.asset_list.item(i).setSelected(True)
                self.asset_list.setCurrentRow(i)
                self.asset_list.setFocus()
                return

    # handles key events for navigating left and right between lists
    def keyPressEvent(self, event):
        print('key pressed')
        key = event.key()

        print('asset_list has focus: {0}'.format(self.asset_list.hasFocus()))
        print('type_list has focus: {0}'.format(self.types_list.hasFocus()))

        if key == QtCore.Qt.Key_Right:
            if self.asset_list.hasFocus():
                # select first selectable type
                self.select_enabled_type()
                return
            elif not self.types_list.hasFocus():
                self.select_enabled_asset()
        elif key == QtCore.Qt.Key_Left:
            if self.types_list.hasFocus():
                self.select_enabled_asset()
                return
            elif not self.asset_list.hasFocus():
                self.select_enabled_type()
        elif key == QtCore.Qt.Key_Escape:
            self.close()

    # ----------------------------------------------------------------------
    # helper functions
    # ----------------------------------------------------------------------
    def enableItem(self, item):
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        item.setTextColor(QtGui.QColor('white'))

    def disableItem(self, item):
        item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEnabled ^ QtCore.Qt.ItemIsSelectable)

    def darkenItem(self, item):
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        item.setTextColor(self.DARK_COLOUR)

    def italicItem(self, item):
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        font = item.font()
        font.setItalic(True)
        item.setFont(font)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    module_path = os.path.dirname(os.path.abspath(__file__))

    app.setStyleSheet(sqss_compiler.compile(
        os.path.join(module_path,'TBA_stylesheet.scss'),
        os.path.join(module_path,'variables.scss'),
    ))

    tba_io_asset_list = TBA_IO_asset_list()

    # this would be called from the parent module
    export_dir = os.path.join(module_path, 'exports', 'assets')
    publish_dir = os.path.join(module_path, '..', '_published3d', 'assets')

    tba_io_asset_list.update_exports_dirs(export_dir, publish_dir)

    # this would be the vfx folder of the job
    tba_io_asset_list.set_root(module_path)

    tba_io_asset_list.show()  # Show the UI
    sys.exit(app.exec_())
