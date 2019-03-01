import subprocess
import os

module_path = os.path.dirname(os.path.abspath(__file__))

exe = os.path.abspath('C:/Python37/Lib/site-packages/PySide2/pyside2-rcc.exe')
qrc = os.path.abspath(os.path.join(module_path, 'TBA_IO.qrc'))
output = os.path.abspath(os.path.join(module_path, 'TBA_IO_resources.py'))


#print(exe)
#print(qrc)
#print(output)
#cmd = ['C:/Python37/Lib/site-packages/PySide2/pyside2-rcc.exe'-o {0} {1}'.format(output, qrc)
cmd = ['C:/Python37/Lib/site-packages/PySide2/pyside2-rcc.exe', '-o', output, qrc]
subprocess.call(cmd)
