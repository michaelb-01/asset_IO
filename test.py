from PySide2 import QtWidgets, QtCore
import sys


class Main(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        pushbutton = QtWidgets.QPushButton('Popup Button')
        menu = QtWidgets.QMenu()
        menu.addAction('This is Action 1', self.Action1)
        menu.addAction('This is Action 2', self.Action2)
        pushbutton.setMenu(menu)
        self.setCentralWidget(pushbutton)

    def Action1(self):
        print('You selected Action 1')

    def Action2(self):
        print('You selected Action 2')


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    main = Main()
    main.show()
    app.exec_()
