from PySide2 import QtCore, QtWidgets
import sys

class MyDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(MyDialog, self).__init__(parent)

        self.setWindowTitle('Modal Dialogs')

        # remove help icon (question mark) from window
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        # create widgets, layouts and connections (signals and slots)
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.frame = QtWidgets.QFrame(self)
        self.frame.setFrameStyle(QtWidgets.QFrame.StyledPanel | QtWidgets.QFrame.Sunken)

        self.combo = QtWidgets.QComboBox()
        self.combo.addItems(['one','two','three'])

        self.combo.setStyleSheet('''QComboBox:on { /* shift the text when the popup opens */
    padding-top: 3px;
    padding-left: 15px;
}''')

    def create_layouts(self):
        # self must be passed to the main_layout so it is parented to the dialog instance
        main_layout = QtWidgets.QVBoxLayout(self.frame)

        main_layout.addWidget(self.combo)

    def create_connections(self):
        pass


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    my_dialog = MyDialog()

    my_dialog.show()  # Show the UI
    sys.exit(app.exec_())
