import sys
import os

from PySide2 import QtCore, QtWidgets, QtGui

sys.dont_write_bytecode = True  # Avoid writing .pyc files

import sqss_compiler
import TBA_UI

class TBA_IO_notes(QtWidgets.QDialog):
    importer = False

    def __init__(self, parent=None):
        super(TBA_IO_notes, self).__init__(parent)

        # unique object name for maya
        self.setObjectName('TBA_IO_notes')

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.header = QtWidgets.QLabel('Notes')

        self.notes = QtWidgets.QPlainTextEdit()

        self.thumbnail_icon = QtGui.QPixmap('icons/take_thumbnail_grey_light.png')
        self.thumbnail_btn = QtWidgets.QPushButton('')
        self.thumbnail_btn.setMinimumSize(130,100)
        self.thumbnail_btn.setIconSize(QtCore.QSize(150,100))
        self.thumbnail_btn.setIcon(self.thumbnail_icon)

    def create_layouts(self):
        # self must be passed to the main_layout so it is parented to the dialog instance
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)

        main_layout.addWidget(self.header)

        notes_layout = QtWidgets.QHBoxLayout()
        notes_layout.addWidget(self.notes)
        notes_layout.addWidget(self.thumbnail_btn)

        main_layout.addLayout(notes_layout)

    def create_connections(self):
        pass

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    module_path = os.path.dirname(os.path.abspath(__file__))

    app.setStyleSheet(sqss_compiler.compile(
        os.path.join(module_path,'TBA_stylesheet.scss'),
        os.path.join(module_path,'variables.scss'),
    ))

    tba_io_notes = TBA_IO_notes()

    tba_io_notes.show()  # Show the UI
    sys.exit(app.exec_())
