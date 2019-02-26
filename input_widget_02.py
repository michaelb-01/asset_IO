import sys

from PySide2 import QtCore, QtWidgets
# from shiboken2 import wrapInstance

try:
  import maya.OpenMayaUI as omui
except:
  print('Not in Maya')

def maya_main_window():
    # get pointer to maya's main window
    main_window_ptr = omui.MQtUtil.mainWindow()
    # return window as a QWidget
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


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
        self.label = QtWidgets.QLabel('Name')
        self.anim_btn = QtWidgets.QPushButton('Animate')

    def create_layouts(self):
        # self must be passed to the main_layout so it is parented to the dialog instance
        main_layout = QtWidgets.QVBoxLayout(self)

        wdg_layout = QtWidgets.QHBoxLayout()
        wdg_layout.addWidget(self.label)
        wdg_layout.addWidget(self.anim_btn)

        main_layout.addLayout(wdg_layout)

    def create_connections(self):
        self.anim_btn.clicked.connect(self.animate)

    def animate(self):
        print('Animate')
        self.anim = QtCore.QPropertyAnimation(self.label, 'geometry')

def run_standalone():
    app = QtWidgets.QApplication(sys.argv)

    my_dialog = MyDialog()

    my_dialog.show()  # Show the UI
    sys.exit(app.exec_())

if __name__ == "__main__":
  run_standalone()
