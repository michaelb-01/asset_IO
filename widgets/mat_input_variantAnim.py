import sys

from PySide2 import QtCore, QtWidgets, QtGui

class AnimateBetweenNums(QtCore.QVariantAnimation):
    def __init__(self):
        QtCore.QVariantAnimation.__init__(self)

    def updateCurrentValue(self, value):
        print value

class DynamicLabel(QtWidgets.QLabel):
    def __init__(self, *args, **kwargs):
        pass

class MyDialog(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MyDialog, self).__init__(parent)

        # create widgets, layouts and connections (signals and slots)
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        self.setFixedSize(400,200)

    def create_widgets(self):
        # self.label = DynamicLabel('Label')
        self.label = QtWidgets.QLabel('Label')

        self.btn10 = QtWidgets.QPushButton('10')
        self.btn70 = QtWidgets.QPushButton('70')

        self.anim = AnimateBetweenNums()
        self.anim.setDuration(1000)
        self.anim.valueChanged.connect(self.updateValue)
        self.value = 50

    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        main_layout.addWidget(self.label)
        main_layout.addWidget(self.btn10)
        main_layout.addWidget(self.btn70)

    def create_connections(self):
        self.btn10.clicked.connect(self.start_anim)

    def start_anim(self):
        print('start anim')
        self.anim.setStartValue(10)
        self.anim.setEndValue(70)
        self.anim.start()

    def updateValue(self, value):
        # self.value = QtCore.QVariant(value).toInt()[0]
        print(value)
        print('update value')
        #self.repaint()

def run_standalone():

    app = QtWidgets.QApplication(sys.argv)

    my_dialog = MyDialog()

    my_dialog.show()  # Show the UI
    sys.exit(app.exec_())

if __name__ == "__main__":
  run_standalone()

