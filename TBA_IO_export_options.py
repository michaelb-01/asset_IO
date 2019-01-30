import sys
import os

from PySide2 import QtCore, QtWidgets, QtGui

sys.dont_write_bytecode = True  # Avoid writing .pyc files

import sqss_compiler
import TBA_UI

class TBA_IO_export_options(QtWidgets.QDialog):
    importer = False

    def __init__(self, parent=None):
        super(TBA_IO_export_options, self).__init__(parent)

        # unique object name for maya
        self.setObjectName('TBA_IO_export_options')

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
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

    def create_layouts(self):
        # self must be passed to the main_layout so it is parented to the dialog instance
        main_layout = QtWidgets.QHBoxLayout(self)

        rb_layout = QtWidgets.QVBoxLayout()

        rb_layout.addWidget(self.rb_curFrame)
        rb_layout.addWidget(self.rb_workRange)
        rb_layout.addWidget(self.rb_startEnd)

        settings_layout = QtWidgets.QVBoxLayout()

        range_layout = QtWidgets.QHBoxLayout()

        range_layout.addWidget(self.range_start_le)
        range_layout.addWidget(self.range_end_le)
        range_layout.addWidget(self.range_step_le)

        settings_layout.addStretch()
        settings_layout.addLayout(range_layout)

        main_layout.addLayout(rb_layout)
        main_layout.addLayout(settings_layout)

    def create_connections(self):
        self.rb_startEnd.toggled.connect(self.on_range_toggled)

    def on_range_toggled(self, checked):
        self.range_start_le.setDisabled(not checked)
        self.range_end_le.setDisabled(not checked)
        self.range_step_le.setDisabled(not checked)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    module_path = os.path.dirname(os.path.abspath(__file__))

    app.setStyleSheet(sqss_compiler.compile(
        os.path.join(module_path,'TBA_stylesheet.scss'),
        os.path.join(module_path,'variables.scss'),
    ))

    tba_io_export_options = TBA_IO_export_options()

    tba_io_export_options.show()  # Show the UI
    sys.exit(app.exec_())
