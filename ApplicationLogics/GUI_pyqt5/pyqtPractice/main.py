# coding: utf-8
'''
1. 테스트 명 : 작성중
    
2. 결과 : 작성중
'''
import sys

from PyQt5.QtWidgets import QApplication
from front import Form

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = Form()
    form.show()
    exit(app.exec_())