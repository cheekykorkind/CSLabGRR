# coding: utf-8
import sys

from PyQt5.QtWidgets import QApplication

from front import Form

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = Form();
    sys.exit(app.exec_())
