# coding: utf-8
import sys

import sys
from PyQt5.QtWidgets import QWidget, QToolTip, QPushButton, QApplication
from PyQt5.QtGui import QFont
from front import Form

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = Form();
    sys.exit(app.exec_())
#         self.resize(250, 150)
#         self.move(300, 300)
#         self.setWindowTitle('Simple')