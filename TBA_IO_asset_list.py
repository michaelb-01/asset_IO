import sys
import os
import subprocess
import shutil

from PySide2 import QtCore, QtWidgets, QtGui

sys.dont_write_bytecode = True  # Avoid writing .pyc files

import sqss_compiler
import TBA_UI

class TBA_IO_asset_list(QtWidgets.QDialog):
    importer = False

    STAGES = ['build','shots','previs','rnd']

    # tasks and their associated formats
    TASKS = {
        'camera':['abc','fbx','mb'],
        'model':['abc','obj','fbx','mb'],
        'anim':['abc','fbx','mb'],
        'fx':['abc','mb'],
        'rig':['mb'],
        'light':['mb']
    }

    # job root
    jobroot = ''

    # maya/nuke/houdini project folder
    workspace = ''

    software = ''

    stage = ''
    entity = ''
    entities = None # available entities for the entity combobox

    # export and publish dirs
    export_dir = ''
    publish_dir = ''

    sel_asset = ''

    DARK_COLOUR = QtGui.QColor(80,85,95)

    def __init__(self, parent=None):
        super(TBA_IO_asset_list, self).__init__(parent)

        # unique object name for maya
        self.setObjectName('TBA_IO_asset_list')

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.home_icon = QtGui.QPixmap('icons/home_white.png')
        self.home_btn = QtWidgets.QPushButton('')
        self.home_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.home_btn.setIcon(self.home_icon)

        self.right_icon = QtGui.QPixmap('icons/arrow_right_white.png')
        self.right_btn = QtWidgets.QPushButton('')
        self.right_btn.setDisabled(True)
        self.right_btn.setIcon(self.right_icon)
        self.right_btn.setFixedWidth(20)
        self.right_btn.setStyleSheet('QPushButton { background-color: none;}')

        self.right_icon2 = QtGui.QPixmap('icons/arrow_right_white.png')
        self.right_btn2 = QtWidgets.QPushButton('')
        self.right_btn2.setDisabled(True)
        self.right_btn2.setIcon(self.right_icon2)
        self.right_btn2.setFixedWidth(20)
        self.right_btn2.setStyleSheet('QPushButton { background-color: none;}')

        self.stage_combo = QtWidgets.QComboBox()
        self.stage_combo.addItems(['shots','builasdfd'])
        self.stage_combo.setCursor(QtCore.Qt.PointingHandCursor)

        self.entity_combo = QtWidgets.QComboBox()
        self.entity_combo.setCursor(QtCore.Qt.PointingHandCursor)

        self.refresh_btn = QtWidgets.QPushButton('')
        self.refresh_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.refresh_icon = QtGui.QPixmap('icons/refresh_white.png')
        self.refresh_btn.setIcon(self.refresh_icon)

        self.asset_list_label = QtWidgets.QLabel('Assets')
        self.asset_list_label.setFixedHeight(35)
        self.asset_list = TBA_UI.TBA_list_draggable()

        self.add_asset_btn = QtWidgets.QPushButton('+')
        self.add_asset_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.add_asset_btn.setStyleSheet('QPushButton { font-size: 20px; width:24px; height:24px; margin:0; padding:0 0 4 1;}')

        self.types_list_label = QtWidgets.QLabel('Tasks')
        self.types_list_label.setFixedHeight(27)
        self.types_list = TBA_UI.TBA_list_draggable()

        for task in self.TASKS:
            item = QtWidgets.QListWidgetItem(task)
            self.disableItem(item)
            self.types_list.addItem(item)

    def create_layouts(self):
        # self must be passed to the main_layout so it is parented to the dialog instance
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)

        # header layout for title and refresh btn
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.addWidget(self.home_btn)
        header_layout.addWidget(self.right_btn)
        header_layout.addWidget(self.stage_combo)
        header_layout.addWidget(self.right_btn2)
        header_layout.addWidget(self.entity_combo)
        header_layout.addStretch()
        header_layout.addWidget(self.refresh_btn)

        # horizontal layout to hold asset and types list
        lists_layout = QtWidgets.QHBoxLayout()

        # asset list layout
        asset_list_layout = QtWidgets.QVBoxLayout()
        asset_list_layout.setSpacing(0)

        asset_list_header_layout = QtWidgets.QHBoxLayout()

        asset_list_header_layout.addWidget(self.asset_list_label)
        asset_list_header_layout.addStretch()
        asset_list_header_layout.addWidget(self.add_asset_btn)

        asset_list_layout.addLayout(asset_list_header_layout)
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
        self.refresh_btn.clicked.connect(self.on_refresh)

        self.add_asset_btn.clicked.connect(self.add_temp_asset)

        #self.work_area.clicked.connect(self.get_work_area)
        #self.stage_btn.clicked.connect(self.on_stage_clicked)

        self.asset_list.itemSelectionChanged.connect(self.on_asset_selected)
        self.asset_list.rightClicked.connect(self.asset_right_clicked)
        # self.asset_list.currentTextChanged.connect(self.test)

        self.stage_combo.activated.connect(self.on_stage_updated)
        self.entity_combo.activated.connect(self.on_entity_updated)

        #self.types_list.itemSelectionChanged.connect(self.on_typ)
        self.types_list.rightClicked.connect(self.asset_right_clicked)

    def set_workspace(self, workspace=None):
        # workspace is set relative to current scene
        print('TBA :: set_workspace')

        if not workspace:
            print('Workspace not found. Exiting')
            return

        self.workspace = workspace

        print('TBA :: workspace is: {0}'.format(self.workspace))

        # split path directories into list
        parts = self.splitall(self.workspace)

        # work up from workspace to find stage and entity
        # we could also work from the vfx folder down since this is common to all jobs
        # but then this tool wont work in a session of maya that is not part of the tba pipeline

        if len(parts) < 3:
            print('TBA :: workspace is not part of the TBA pipeline')
        else:
            self.software = parts[-1]
            self.entity = parts[-2]
            self.stage = parts[-3]
            # the job root is up to 'stage'
            self.jobroot = os.path.join(*parts[:-3])

            print('TBA :: stage is: {0}'.format(self.stage))
            print('TBA :: entity is: {0}'.format(self.entity))
            print('TBA :: software is: {0}'.format(self.software))
            print('TBA :: jobroot is: {0}'.format(self.jobroot))

        self.get_export_dirs()

        # initilaize stage and entity combo
        # self.stage_combo.clear()
        # self.stage_combo.addItem(self.stage)

        # self.entity_combo.clear()
        # self.entity_combo.addItem(self.entity)

        self.update_breadcrumbs()

    def update_workspace(self):
        print('TBA :: update_workspace')
        self.workspace = os.path.join(self.jobroot, self.stage, self.entity, self.software)
        self.get_export_dirs()

    def get_export_dirs(self):
        print('TBA :: get_export_dirs')

        if not self.workspace:
            print('No workspace specified')
            return

        print('TBA :: get_export_dirs, workspace is: {0}'.format(self.workspace))

        export_dir = os.path.join(self.workspace, 'exports', 'assets')
        publish_dir = os.path.join(self.workspace, '..', '_published3d', 'assets')

        missing_dirs = []

        msg = ''

        if not os.path.exists(export_dir):
            missing_dirs.append(export_dir)
        if not os.path.exists(publish_dir):
            missing_dirs.append(publish_dir)

        if missing_dirs:
            msg = 'Export folders are missing. Create them?\n\n' + '\n\n'.join(missing_dirs)

            res = QtWidgets.QMessageBox.question(self, "Export folders are missing", msg,
                                    QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)

            if res == QtWidgets.QMessageBox.Cancel:
                return

            for directory in missing_dirs:
                try:
                    os.makedirs(directory)
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        raise

        if export_dir != self.export_dir or publish_dir != self.publish_dir:
            self.export_dir = export_dir
            self.publish_dir = publish_dir

            self.update_asset_list()

    def update_breadcrumbs(self):
        print('TBA :: update_breadcrumbs')
        self.update_stages_combo()

    def update_stages_combo(self):
        print('TBA :: update_stages_combo')

        # store currently selected item
        selItem = self.stage_combo.currentText()

        # clear combo
        self.stage_combo.clear()

        # update stages combo
        stages_dir = self.jobroot

        stages = []

        if os.path.exists(stages_dir):
            stages = sorted(os.listdir(stages_dir))
        else:
            print('TBA :: stages_dir does not exists: {0}'.format(stages_dir))

        for stage in stages:
            if not stage.startswith('.'):
                self.stage_combo.addItem(stage)

        # reselect old stage if found
        if selItem in stages:
            self.stage_combo.setCurrentText(selItem)
        elif self.stage in stages:
            # select currently selected stage
            self.stage_combo.setCurrentText(self.stage)
        else:
            # otherwise set to the first item in the list
            self.stage = stages[0]

        # update width to fit items
        # width = self.stage_combo.minimumSizeHint().width()
        # self.stage_combo.view().setMinimumWidth(width+10)
        self.update_entities_combo()

    def update_entities_combo(self):
        print('TBA :: update_entities_combo')

        # store currently selected item
        selEntity = self.entity_combo.currentText()

        print('TBA :: old entity: {0}'.format(selEntity))

        # clear combo
        self.entity_combo.clear()

        # update stages combo
        entities_dir = os.path.join(self.jobroot, self.stage)

        entities = []

        if os.path.exists(entities_dir):
            #entities = sorted(os.listdir(entities_dir))
            entities = sorted([f for f in os.listdir(entities_dir) if not f.startswith('.')])
        else:
            print('TBA :: entities_dir does not exists: {0}'.format(entities_dir))

        print('TBA :: found entities in stage: {0}'.format(entities))

        for entity in entities:
            if not entity.startswith('.'):
                self.entity_combo.addItem(entity)

        # reselect old entity if found
        if selEntity in entities:
            self.entity = selEntity
            self.entity_combo.setCurrentText(selEntity)
        # select currently selected entity
        elif self.entity in entities:
            self.entity_combo.setCurrentText(self.entity)
        else:
            # otherwise set to the first item in the list
            self.entity = entities[0]

        # if entity has changed we need to update the workspace (and asset list)
        print('TBA :: new entity: {0}'.format(self.entity))

        if selEntity != self.entity:
            self.update_workspace()

    def on_stage_updated(self, stage):
        # ensure text is correct - doesnt seem to pass the correct result when triggered programatically
        stage = self.stage_combo.currentText()
        print('TBA :: on_stage_updated: {0}'.format(stage))

        if stage != self.stage:
            self.stage = stage

            self.update_entities_combo()

    def on_entity_updated(self, entity):
        # ensure text is correct - doesnt seem to pass the correct result when triggered programatically
        entity = self.entity_combo.currentText()
        print('on_entity_updated: {0}'.format(entity))

        if entity != self.entity:
            self.entity = entity
            self.update_workspace()

    def on_refresh(self):
        if not self.workspace:
            print('TBA :: workspace not set, exiting')
            return

        self.update_asset_list()
        self.update_breadcrumbs()

    def add_temp_asset(self):
        # check if editable item already exists
        for i in range(0, self.asset_list.count()):
            item = self.asset_list.item(i)
            if item.flags() & QtCore.Qt.ItemIsEditable:
                item.setSelected(True)
                self.asset_list.editItem(item)
                return

        item = QtWidgets.QListWidgetItem('')
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
        
        self.asset_list.addItem(item)
        self.asset_list.setFocus()

        item.setSelected(True)

        self.asset_list.editItem(item)

        self.asset_list.itemDelegate().commitData.connect(self.temp_asset_edited)

    def temp_asset_edited(self):
        print('temp asset edited')

        if not self.asset_list.selectedItems():
            return

        temp_item = self.asset_list.selectedItems()[0]

        # remove if empty
        if not temp_item.text():
            self.asset_list.takeItem(self.asset_list.row(temp_item))

        # remove item if its name already exists
        found = self.asset_list.findItems(temp_item.text(), QtCore.Qt.MatchExactly)

        # always returns itself, so more than 1 means its found another
        if len(found) > 1:
            self.asset_list.takeItem(self.asset_list.row(temp_item))

        self.on_asset_selected()

    def check_temp_asset(self, text):
        print('TBA :: check_temp_asset')
        print(text)

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

        # if user deselected the item
        if not self.asset_list.selectedItems():
            print('on_asset_selected: set sel_asset to None')
            self.sel_asset = None
        else:
            self.sel_asset = self.asset_list.selectedItems()[0].text()
            print('on_asset_selected: set sel_asset to {0}'.format(self.sel_asset))

        # update type list
        self.updateTypeList()
        self.clearList(self.types_list)
        #self.select_enabled_type()

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

    def asset_right_clicked(self, eventlist):
        print('TBA :: asset_right_clicked')

        print('TBA :: selAsset: {0}'.format(self.sel_asset))

        item = eventlist[0]
        pos = eventlist[1]

        contextMenu = QtWidgets.QMenu(self)
        contextMenu.setCursor(QtCore.Qt.PointingHandCursor)

        exploreAct = contextMenu.addAction('Explore Exports Asset')
        deleteAct = contextMenu.addAction('Delete Exports Asset')
        nullAct = contextMenu.addAction('-')
        nullAct.setSeparator(True)
        explorePubAct = contextMenu.addAction('Explore Published Asset')
        deletePubAct = contextMenu.addAction('Delete Published Asset')

        action = contextMenu.exec_(pos)

        # path to asset

        if action == exploreAct:
            self.exploreFile(os.path.join(self.export_dir,item.text()))
        elif action == deleteAct:
            self.deleteAsset(os.path.join(self.export_dir,item.text()))
        elif action == explorePubAct:
            self.exploreFile(os.path.join(self.publish_dir,item.text()))
        elif action == deletePubAct:
            self.deleteAsset(os.path.join(self.publish_dir,item.text()))

    def exploreFile(self, asset_path):
        print('exploreFile')
        if not os.path.exists(asset_path):
            print('Asset does not exists at: {0}'.format(asset_path))
            return

        if sys.platform == "win32":
            print('Explore file in windows explorer')
            subprocess.Popen(r'explorer /select, ' + asset_path)
        elif sys.platform == "darwin":
            print('Explore file in mac finder')
            subprocess.Popen(["open", asset_path])
        else:
            print('OS is linux, ignoring..')

    def deleteAsset(self, asset_path):
        print('deleteAsset')
        if not os.path.exists(asset_path):
            print('Asset does not exists at: {0}'.format(asset_path))
            return

        res = QtWidgets.QMessageBox.question(self, "You are about to delete an asset on disk!", "Are you sure?",
                                QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)

        if res == QtWidgets.QMessageBox.Ok:
            print('Deleting: {0}'.format(asset_path))

            try:
                shutil.rmtree(asset_path)
            except OSError as e:
                print ("Error: %s - %s." % (e.asset_path, e.strerror))
            else:
                print('Successfully deleted: {0}'.format(asset_path))
                self.update_asset_list()

    def clearList(self, listwidget):
        for i in range(listwidget.count()):
            item = listwidget.item(i)
            listwidget.setItemSelected(item, False)

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
    def splitall(self, path):
        allparts = []
        while 1:
            parts = os.path.split(path)
            if parts[0] == path:  # sentinel for absolute paths
                allparts.insert(0, parts[0])
                break
            elif parts[1] == path: # sentinel for relative paths
                allparts.insert(0, parts[1])
                break
            else:
                path = parts[0]
                allparts.insert(0, parts[1])
        return allparts

    def disableAllTypes(self):
        print('disableAllTypes')
        # disable all type items
        if self.importer:
            for i in range(self.types_list.count()):
                self.disableItem(self.types_list.item(i))
        else:
            for i in range(self.types_list.count()):
                self.darkenItem(self.types_list.item(i))

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
    workspace = os.path.join(module_path, 'vfx', 'shots', 'sh0001', 'maya')
    export_dir = os.path.join(module_path, 'exports', 'assets')
    publish_dir = os.path.join(module_path, '..', '_published3d', 'assets')

    # workspace
    tba_io_asset_list.set_workspace(workspace)
    #tba_io_asset_list.update_exports_dirs(export_dir, publish_dir)

    # this would be the vfx folder of the job
    #tba_io_asset_list.set_root(module_path)

    tba_io_asset_list.show()  # Show the UI
    sys.exit(app.exec_())
