import sys

from PySide2 import QtWidgets, QtCore

class MyWindow(QtWidgets.QWidget):
    """docstring for MyWindow"""
    def __init__(self, parent=None):
        super(MyWindow, self).__init__()

        self.path = 'S:/CLIENT_JOBS/TIME_BASED_ARTS/0907TBA_1018_RnD/vfx/shots/sh0001'

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.model = QtWidgets.QFileSystemModel()
        # filter by directories only (QDir.Files for files), ignore files beginning with dots
        self.model.setFilter(QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot)

        # set root path
        index = self.model.setRootPath(self.path)

        self.combo = QtWidgets.QComboBox()
        self.combo.setModel(self.model)
        self.combo.setRootModelIndex(index)

    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        main_layout.addWidget(self.combo)

    def create_connections(self):
        pass

def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MyWindow()
    win.resize(400,100)
    win.show()
    win.raise_()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
