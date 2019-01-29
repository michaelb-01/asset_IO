import sys
import os

from PySide2 import QtWidgets, QtGui, QtCore

import sqss_compiler

class ThumbListWidget(QtWidgets.QListWidget):
    def __init__(self, parent=None):
        super(ThumbListWidget, self).__init__(parent)
        self.setIconSize(QtCore.QSize(124, 124))
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            super(ThumbListWidget, self).dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            super(ThumbListWidget, self).dragMoveEvent(event)

    def dropEvent(self, event):
        print('dropEvent', event)
        if event.mimeData().hasUrls():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            links = []
            for url in event.mimeData().urls():
                links.append(str(url.toLocalFile()))
            self.emit(QtCore.SIGNAL("dropped"), links)
        else:
            event.setDropAction(QtCore.Qt.MoveAction)
            super(ThumbListWidget, self).dropEvent(event)


class TBA_IO_asset_list(QtWidgets.QDialog):
    # tasks and their associated formats
    TASKS = {
        'camera':['abc','fbx','mb'],
        'model':['abc','obj','fbx','mb'],
        'anim':['abc','fbx','mb'],
        'fx':['abc','mb'],
        'rig':['mb'],
        'light':['mb']
    }

    # export and publish dirs
    export_dir = None
    publish_dir = None

    def __init__(self, parent=None):
        super(TBA_IO_asset_list, self).__init__(parent)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.asset_list = ThumbListWidget(self)
        for i in range(12):
            item = QtWidgets.QListWidgetItem( 'Item '+ str(i) )
            self.asset_list.addItem(item)

        self.types_list = ThumbListWidget(self)

    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        lists_layout = QtWidgets.QHBoxLayout()

        asset_list_layout = QtWidgets.QVBoxLayout()
        asset_list_layout.addWidget(self.asset_list)

        type_list_layout = QtWidgets.QVBoxLayout()
        type_list_layout.addWidget(self.types_list)

        lists_layout.addLayout(asset_list_layout)
        lists_layout.addLayout(type_list_layout)

        main_layout.addLayout(lists_layout)

    def create_connections(self):
        self.connect(self.asset_list, QtCore.SIGNAL("dropped"), self.items_dropped)
        self.asset_list.currentItemChanged.connect(self.item_clicked)

        self.connect(self.types_list, QtCore.SIGNAL("dropped"), self.items_dropped)
        self.types_list.currentItemChanged.connect(self.item_clicked)

    def items_dropped(self, arg):
        print('items_dropped', arg)

    def item_clicked(self, arg):
        print(arg)

    def update_exports_dirs(self, export_dir=None, publish_dir=None):
        print('TBA :: update_exports_dirs')

        print('Export directory: {0}'.format(export_dir))
        print('Publish directory: {0}'.format(publish_dir))

        self.export_dir = export_dir
        self.publish_dir = publish_dir

        # update asset list
        self.update_asset_list()

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

            self.disableItem(item)

            # reselect item if it was previously selected
            if asset == sel_asset:
                item.setSelected(True)

            # add item
            self.asset_list.addItem(item)



    # ----------------------------------------------------------------------
    # helper functions
    # ----------------------------------------------------------------------
    def disableItem(self, item):
        item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEnabled ^ QtCore.Qt.ItemIsSelectable)

    def italicItem(self, item):
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        font = item.font()
        font.setItalic(True)
        item.setFont(font)


if __name__ == '__main__':
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

    tba_io_asset_list.show()
    tba_io_asset_list.resize(480,320)
    sys.exit(app.exec_())
