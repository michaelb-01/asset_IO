from PySide2 import QtCore, QtWidgets
import sys

class MyDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(MyDialog, self).__init__(parent)

        self.setWindowTitle('Modal Dialogs')
        self.setMinimumSize(300,80)

        # remove help icon (question mark) from window
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        # create widgets, layouts and connections (signals and slots)
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.combo = QtWidgets.QComboBox()
        self.combo.addItems(['one','two','three'])

    def create_layouts(self):
        # self must be passed to the main_layout so it is parented to the dialog instance
        main_layout = QtWidgets.QVBoxLayout(self)

        main_layout.addWidget(self.combo)

    def create_connections(self):
        pass


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    my_dialog = MyDialog()

    my_dialog.show()  # Show the UI
    sys.exit(app.exec_())