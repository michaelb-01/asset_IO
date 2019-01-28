import sys
import os

import sqss_compiler

from PySide2 import QtCore, QtWidgets, QtGui

class TBA_IO_assetList(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(TBA_IO_common, self).__init__(parent)

        print('TBA_IO_common')

if __name__ == "__main__":
    print('TBA :: Run Standalone')
    app = QtWidgets.QApplication(sys.argv)

    module_path = os.path.dirname(os.path.abspath(__file__))

    app.setStyleSheet(sqss_compiler.compile(
        os.path.join(module_path,'TBA_stylesheet.scss'),
        os.path.join(module_path,'variables.scss'),
    ))

    tba_io_common = TBA_IO_common()

    tba_io_common.show()  # Show the UI
    sys.exit(app.exec_())
