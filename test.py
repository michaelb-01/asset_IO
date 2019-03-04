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
        self.list = QtWidgets.QListWidget()

        for name in ['one','tow','three']:
            item = QtWidgets.QListWidgetItem(name, self.list)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEditable)
            self.list.addItem(item)

    def create_layouts(self):
        # self must be passed to the main_layout so it is parented to the dialog instance
        main_layout = QtWidgets.QHBoxLayout(self)

        main_layout.addWidget(self.list)

        self.setGeometry(100, 100, 500, 500)

    def create_connections(self):
        self.list.itemChanged.connect(self.edited)

    def edited(self, item):
        print('edited')

        asset = item.data(QtCore.Qt.UserRole)
        item.setData(QtCore.Qt.UserRole, 'hello')

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    my_dialog = MyDialog()

    my_dialog.show()  # Show the UI
    sys.exit(app.exec_())
