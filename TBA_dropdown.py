import sys
from PySide2 import QtCore, QtGui, QtWidgets

import sqss_compiler

class Example(QtWidgets.QWidget):
    
    def __init__(self):
        super(Example, self).__init__()
        
        self.initUI()
        
    def initUI(self):      

        # self.lbl = QtWidgets.QLabel("Ubuntu", self)

        combo = QtWidgets.QComboBox(self)
        combo.addItem("Ubuntu")
        combo.addItem("Mandriva")
        combo.addItem("Fedora")
        combo.addItem("Red Hat")
        combo.addItem("Gentoo")

        # combo.move(50, 50)
        # self.lbl.move(50, 150)

        # combo.activated[str].connect(self.onActivated)        
         
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('TBA Dropdown')
        self.show()
        
    # def onActivated(self, text):
    #     self.lbl.setText(text)
    #     self.lbl.adjustSize()   
        
def main():
    app = QtWidgets.QApplication(sys.argv)
    # set default styling
    app.setStyleSheet(sqss_compiler.compile('TBA_stylesheet.scss', 'variables.scss'))

    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()