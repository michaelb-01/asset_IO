import sys

from PySide2 import QtCore, QtWidgets, QtGui

class MyDialog(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MyDialog, self).__init__(parent)

        # create widgets, layouts and connections (signals and slots)
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.header = QtWidgets.QLabel('Properties')
        self.name = QtWidgets.QLabel('My Asset')
        self.name.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.name.setStyleSheet('background-color: red;')

    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        main_layout.addWidget(self.header)

        form_group = QtWidgets.QGroupBox("Form layout")
        form_group.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        form_layout = QtWidgets.QFormLayout()
        form_layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        form_layout.addRow(QtWidgets.QLabel("Name:"), self.name)
        form_layout.addRow(QtWidgets.QLabel("agagag:"), self.name)
        form_layout.addRow(QtWidgets.QLabel("sd:"), self.name)
        # form_group.setLayout(form_layout)



        main_layout.addLayout(form_layout)
        # main_layout.addWidget(self.name)

    def create_connections(self):
        pass

def run_standalone():

    app = QtWidgets.QApplication(sys.argv)

    my_dialog = MyDialog()

    my_dialog.show()  # Show the UI
    sys.exit(app.exec_())

if __name__ == "__main__":
  run_standalone()

