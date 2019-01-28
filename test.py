import sys
from PySide2 import QtWidgets, QtCore

class Test(QtWidgets.QDialog):
    def __init__(self):
        super(Test, self).__init__()

        test = QtWidgets.QLabel('Test')

        msgBox = QtWidgets.QMessageBox(self)
        msgBox.setText("Could not find folder")
        msgBox.setInformativeText("Create it?")
        msgBox.setStandardButtons( QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel )
        msgBox.setDefaultButton( QtWidgets.QMessageBox.Ok )

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(test)
        main_layout.addWidget(msgBox)

        res = msgBox.exec_();

        print(res)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    test = Test()

    test.show()  # Show the UI
    sys.exit(app.exec_())
