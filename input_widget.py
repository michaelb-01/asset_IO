import sys

from PySide2 import QtCore, QtWidgets, QtGui
# from shiboken2 import wrapInstance

# import maya.OpenMayaUI as omui

def maya_main_window():
    # get pointer to maya's main window
    main_window_ptr = omui.MQtUtil.mainWindow()
    # return window as a QWidget
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

class StretchedLabel(QtWidgets.QLabel):
    def __init__(self, *args, **kwargs):
        QtWidgets.QLabel.__init__(self, *args, **kwargs)
        #self.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        self.setGeometry(QtCore.QRect(0,0,100,20))

    def resizeEvent(self, evt):
        #print self.height()
        font = self.font()
        #print font.pixelSize()
        font.setPixelSize(self.height())
        self.setFont(font)

class StretchedLabel2(QtWidgets.QLabel):
    def __init__(self, *args, **kwargs):
        QtWidgets.QLabel.__init__(self, *args, **kwargs)
        #self.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)

    def resizeEvent(self, evt):
        font = self.font()
        font.setPixelSize(self.height() * 0.8)
        self.setFont(font)

class TBAInput(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(TBAInput, self).__init__(parent)

        # create widgets, layouts and connections (signals and slots)
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        label_pos1 = QtCore.QRect(0, 0, 100, 30)

        self.toggled = False

    def create_widgets(self):
        # self.label = QtWidgets.QLabel('Name')
        self.label = QtWidgets.QLabel('Name')
        #self.label.setStyleSheet("QWidget { background-color: rgb(255, 198, 201); }")
        # self.label.setGeometry(self.label_pos1)
        self.lineedit = QtWidgets.QLineEdit()
        self.btn = QtWidgets.QPushButton('Animate')

    def create_layouts(self):
        # self must be passed to the main_layout so it is parented to the dialog instance
        main_layout = QtWidgets.QVBoxLayout(self)

        main_layout.addWidget(self.label)
        main_layout.addWidget(self.lineedit)
        main_layout.addWidget(self.btn)

    def create_connections(self):
      self.btn.clicked.connect(self.animate_label)

    def test(self):
      self.timer = QtCore.QTimer(self)
      # self.timer.setSingleShot(True)
      # self.timer.setInterval(20)

      self.timer.timeout.connect(self.tick)
      self.timer.setSingleShot(True)
      self.timer.start(300)
      # self.timer.setInterval(3000)
      # self.timer.start()

    def tick(self):
      print('tick')
      self.label.move(self.label.pos() + QtCore.QPoint(0, 1))
      print(self.timer.remainingTime())

    def animate_label(self):
      self.anim = QtCore.QPropertyAnimation(self,"color")
      # self.move_anim.setDuration(150)

      # rect = self.label.geometry()

      # if self.toggled:
      #   size = 10
      # else:
      #   size = 20

      # self.toggled = not self.toggled

      # print("Animate from {0} to {1}".format(rect.height(), size))

      # self.move_anim.setStartValue(QtCore.QRect(0, 0, 100, rect.height()))
      # self.move_anim.setEndValue(QtCore.QRect(0, 0, 100, size))
      # self.move_anim.setEasingCurve(QtCore.QEasingCurve.InOutCubic)

      self.move_anim.start()

class MyDialog(QtWidgets.QDialog):
    # set parent of widget as maya's main window
    # this means the widget will stay on top of maya
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
        self.close_btn = QtWidgets.QPushButton('Close')
        self.name_input = TBAInput()

    def create_layouts(self):
        # self must be passed to the main_layout so it is parented to the dialog instance
        main_layout = QtWidgets.QVBoxLayout(self)

        wdg_layout = QtWidgets.QHBoxLayout()
        wdg_layout.addWidget(self.name_input)
        wdg_layout.addWidget(self.close_btn)

        main_layout.addLayout(wdg_layout)

    def create_connections(self):
        self.close_btn.clicked.connect(self.close)

def run_standalone():

    app = QtWidgets.QApplication(sys.argv)

    my_dialog = MyDialog()

    my_dialog.show()  # Show the UI
    sys.exit(app.exec_())

if __name__ == "__main__":
  run_standalone()

