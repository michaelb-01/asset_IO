import sys
import os

from PySide2 import QtCore, QtWidgets, QtGui

sys.dont_write_bytecode = True  # Avoid writing .pyc files

import sqss_compiler

class TBA_job_builder(QtWidgets.QDialog):
    SERVERS = [
        { 'value':'S:', 'label':'Server1' },
        { 'value':'X:', 'label':'Server2' },
        { 'value':'Y:', 'label':'Server3' }
    ]

    def __init__(self, parent=None):
        super(TBA_job_builder, self).__init__(parent)

        # unique object name for maya
        self.setObjectName('TBA_job_builder')

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.server_combo = QtWidgets.QComboBox()
        self.client = QtWidgets.QLineEdit()
        self.agency = QtWidgets.QLineEdit()
        self.job_name = QtWidgets.QLineEdit()

        self.mode_toggle = QtWidgets.QCheckbox()

        self.update_button = QtWidgets.QPushButton('Update')
        self.update_button.setCursor(QtCore.Qt.PointingHandCursor)
        self.update_button.hide()

        self.create_button = QtWidgets.QPushButton('Create')
        self.create_button.setCursor(QtCore.Qt.PointingHandCursor)

        self.file_dialog_btn = QtWidgets.QPushButton('Browse')
        self.file_dialog_btn.setCursor(QtCore.Qt.PointingHandCursor)

        for server in self.SERVERS:
            # item.setData(server.label, QtCore.Qt.DisplayRole)
            self.server_combo.addItem(server['label']  + ' (' + server['value'] + ')', server['value'])

    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        form_layout = QtWidgets.QFormLayout()
        form_layout.setLabelAlignment(QtCore.Qt.AlignLeft)

        form_layout.addRow('Server*:', self.server_combo)
        form_layout.addRow('Client*:', self.client)
        form_layout.addRow('Agency*:', self.agency)
        form_layout.addRow('Job Name*:', self.job_name)

        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.update_button)
        main_layout.addWidget(self.create_button)
        main_layout.addWidget(self.file_dialog_btn)

    def create_connections(self):
        self.file_dialog_btn.clicked.connect(self.open_file_dialog)

    def open_file_dialog(self):
        self.file_dialog = QtWidgets.QFileDialog()
        self.file_dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)

        if self.file_dialog.exec_():
            initial_path = "S:/"
            path = QtWidgets.QFileDialog().getExistingDirectory(self, "Choose Existing Job", initial_path, QtWidgets.QFileDialog.DirectoryOnly)
            # path = self.file_dialog.getExistingDirectory(self, "Choose Existing Job", initial_path, QtWidgets.QFileDialog.DirectoryOnly)

            self.parse_job(path)
        # self.file_dialog.setFilter("Text files (*.txt)")

    def parse_job(self, path):
        print(path)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    module_path = os.path.dirname(os.path.abspath(__file__))

    app.setStyleSheet(sqss_compiler.compile(
        os.path.join(module_path,'TBA_stylesheet.scss'),
        os.path.join(module_path,'variables.scss'),
    ))

    tba_job_builder = TBA_job_builder()

    tba_job_builder.show()  # Show the UI
    sys.exit(app.exec_())
