import sys
import os

from PySide2 import QtCore, QtWidgets, QtGui

try:
    import maya.cmds as mc
    import maya.OpenMayaUI as omui
    from shiboken2 import wrapInstance
    import maya_api
    MAYA = True
except ImportError:
    MAYA = False

import sqss_compiler
import TBA_UI

import TBA_IO_notes
import TBA_IO_collection_list

sys.dont_write_bytecode = True  # Avoid writing .pyc files

def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

class MayaListWidget(QtWidgets.QListWidget):
    """ Subclass of QListWidget to support Drag and Drop in Maya. """

    def __init__(self):
        super(MayaListWidget, self).__init__()

        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        """ Reimplementing event to accept plain text, """
        if event.mimeData().hasFormat('text/plain'):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """ Reimplementing event to accept plain text, """
        if event.mimeData().hasFormat('text/plain'):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """ """
        print("Dropped!")
        print(event.mimeData().text())
        print(type(event.mimeData().text()))

class TBA_IO_object_list(QtWidgets.QDialog):
    importer = False

    def __init__(self, parent=None):
        super(TBA_IO_object_list, self).__init__(parent)

        # unique object name for maya
        self.setObjectName('TBA_IO_object_list')

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.header = QtWidgets.QLabel('Objects')
        self.header.setFixedHeight(24)

        self.list = MayaListWidget()

        self.add_btn = QtWidgets.QPushButton('Add')
        self.remove_btn = QtWidgets.QPushButton('Remove')

    def create_layouts(self):
        # self must be passed to the main_layout so it is parented to the dialog instance
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)

        object_layout = QtWidgets.QVBoxLayout()
        object_layout.addWidget(self.header)
        object_layout.addWidget(self.list)

        btn_layout = QtWidgets.QVBoxLayout()
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.remove_btn)

        main_layout.addLayout(object_layout)
        main_layout.addLayout(btn_layout)

    def create_connections(self):
        self.add_btn.clicked.connect(self.add_selected)
        self.remove_btn.clicked.connect(self.remove_selected)

    def add_selected(self):
        print('add')
        objs = mc.ls(sl=True, transforms=True, long=True)

        for obj in objs:
            items = self.list.findItems(obj, QtCore.Qt.MatchExactly)

            if not items:
                self.list.addItem(obj)

    def remove_selected(self):
        objs = mc.ls(sl=True, transforms=True, long=True)

        for obj in objs:
            items = self.list.findItems(obj, QtCore.Qt.MatchExactly)

            for item in items:
                row = self.list.row(item)
                self.list.takeItem(row)

        print('add')

def run_standalone():
    app = QtWidgets.QApplication(sys.argv)

    module_path = os.path.dirname(os.path.abspath(__file__))

    app.setStyleSheet(sqss_compiler.compile(
        os.path.join(module_path,'TBA_stylesheet.scss'),
        os.path.join(module_path,'variables.scss'),
    ))

    tba_io_object_list = TBA_IO_object_list()

    tba_io_object_list.show()  # Show the UI
    sys.exit(app.exec_())

def run_maya():
    try:
        tba_io_object_list.close() # pylint: disable=E0601
        tba_io_object_list.deleteLater()
    except:
        pass

    tba_io_object_list = TBA_IO_object_list(maya_main_window())
    tba_io_object_list.show()

if __name__ == "__main__":
    if MAYA:
        run_maya()
    else:
        run_standalone()
