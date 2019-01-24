import sys

from PySide2 import QtCore, QtGui, QtWidgets

class exporter(QtWidgets.QDialog):

  def __init__(self, parent=None):
    super(exporter, self).__init__()

    # create window on inherited widget
    self.setWindowTitle('TBA Exporter')

    self.resize(800, 300)

    # create widgets, layouts and connections (signals and slots)
    self.create_widgets()
    self.create_layouts()
    self.create_connections()

    self.show()

  def create_widgets(self):
      self.close_btn = QtWidgets.QPushButton('Close')
              
  def create_layouts(self):
      # self must be passed to the main_layout so it is parented to the dialog instance
      main_layout = QtWidgets.QVBoxLayout(self)
      
      wdg_layout = QtWidgets.QHBoxLayout()
      wdg_layout.addStretch()
      wdg_layout.addWidget(self.close_btn)

      main_layout.addLayout(wdg_layout)
      # set mainLayout as the main layout
      self.setLayout(main_layout)
      
  def create_connections(self):
      self.close_btn.clicked.connect(self.close)

def main():
  app = QtWidgets.QApplication(sys.argv)

  tba = exporter()

  sys.exit(app.exec_())

if __name__ == '__main__':
  main()