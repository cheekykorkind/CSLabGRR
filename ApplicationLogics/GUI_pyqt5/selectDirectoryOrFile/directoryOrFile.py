# coding: utf-8
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog

# 파일 선택
def selectFile(QWidget):    
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    fileName, _ = QFileDialog.getOpenFileName(QWidget,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
    if fileName:
        print(fileName)
# 디렉토리 선택
def selectDirectory(QWidget):
    dialog = QFileDialog()
    folder_path = dialog.getExistingDirectory(None, "Select Folder")
    print(folder_path)
    
if __name__ == '__main__':
    
    app = QApplication(sys.argv)

    w = QWidget()
    w.resize(250, 150)
    w.move(300, 300)
    w.setWindowTitle('sample')
    selectDirectory(w)
#     selectFile(w)
    w.show()
    
    sys.exit(app.exec_())
    
        