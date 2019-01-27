import sys

from PySide2 import QtCore, QtWidgets, QtGui
# from shiboken2 import wrapInstance

# import maya.OpenMayaUI as omui

def maya_main_window():
    # get pointer to maya's main window
    main_window_ptr = omui.MQtUtil.mainWindow()
    # return window as a QWidget
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

class DynamicLabel(QtWidgets.QLabel):
    def __init__(self, *args, **kwargs):
        QtWidgets.QLabel.__init__(self, *args, **kwargs)
        self.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)

        self.setStyleSheet("background-color: grey;")

        self.anim = QtCore.QPropertyAnimation(self,'geometry')
        self.anim.setDuration(300)
        self.anim.setEasingCurve(QtCore.QEasingCurve.InOutCubic)

        self.rect = None

        self.toggled = False

        self.small = QtCore.QRect(0,0,200,10)
        self.big = QtCore.QRect(10,10,200,50)

        self.myfont = self.font() 

        # self.move(self.big.x(), self.big.y())
        # self.resize(self.big.width(),self.big.height())
        # self.setMinimumHeight(self.small.height())
        # self.setMaximumHeight(self.big.height())
        self.setBaseSize(QtCore.QSize(self.big.width(), self.big.height()))
        self.updateGeometry()
        self.setGeometry(10,10,300,50)

        print('Height: {0}'.format(self.sizeHint().height()))
        print('Width: {0}'.format(self.sizeHint().width()))

    def resizeEvent(self, evt):
        height = evt.size().height()
        print('Resizing, height: {0}'.format(evt.size().height()))

        self.myfont.setPixelSize(height)
        self.setFont(self.myfont)

        if self.rect:
            self.resize(self.rect.width(), height)

    def toggle(self):
        if not self.rect:
            self.rect = self.geometry()

        if self.toggled:
            start = self.small
            end = self.big
        else:
            start = self.big
            end = self.small

        self.anim.setStartValue(start)
        self.anim.setEndValue(end)
        
        self.anim.start()

        self.toggled = not self.toggled

class MyDialog(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MyDialog, self).__init__(parent)

        # create widgets, layouts and connections (signals and slots)
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        self.setFixedSize(400,200)

    def create_widgets(self):
        self.label = DynamicLabel('Label')

        self.btn = QtWidgets.QPushButton('Animate')

    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        main_layout.addWidget(self.label)
        main_layout.addWidget(self.btn)

    def create_connections(self):
      self.btn.clicked.connect(self.label.toggle)

def run_standalone():

    app = QtWidgets.QApplication(sys.argv)

    my_dialog = MyDialog()

    my_dialog.show()  # Show the UI
    sys.exit(app.exec_())

if __name__ == "__main__":
  run_standalone()

