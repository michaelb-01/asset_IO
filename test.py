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
        pass

    def create_layouts(self):
        # self must be passed to the main_layout so it is parented to the dialog instance
        main_layout = QtWidgets.QHBoxLayout(self)

        splitter1 = QtWidgets.QSplitter(self)
        splitter1.setOrientation(QtCore.Qt.Horizontal)

        left = QtWidgets.QFrame(splitter1)
        left.setFrameShape(QtWidgets.QFrame.StyledPanel)

        center = QtWidgets.QFrame(splitter1)
        center.setFrameShape(QtWidgets.QFrame.StyledPanel)

        # splitter2 = QtWidgets.QSplitter(splitter1)
        # sizePolicy = splitter2.sizePolicy()
        # sizePolicy.setHorizontalStretch(1)

        # splitter2.setSizePolicy(sizePolicy)
        # splitter2.setOrientation(QtCore.Qt.Vertical)

        # top_right = QtWidgets.QFrame(splitter2)
        # top_right.setFrameShape(QtWidgets.QFrame.StyledPanel)
        # bottom_right = QtWidgets.QFrame(splitter2)
        # bottom_right.setFrameShape(QtWidgets.QFrame.StyledPanel)

        main_layout.addWidget(splitter1)

        self.setGeometry(100, 100, 500, 500)

    def create_connections(self):
        pass


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    my_dialog = MyDialog()

    my_dialog.show()  # Show the UI
    sys.exit(app.exec_())
