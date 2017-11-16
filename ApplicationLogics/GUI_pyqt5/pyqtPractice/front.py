# coding: utf-8
import sys

from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QSpacerItem
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QGroupBox

from PyQt5.QtWidgets import QBoxLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QFormLayout

from PyQt5.QtWidgets import QListView
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtGui import QStandardItem

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSlot


class Form(QWidget):
    def __init__(self):
        QWidget.__init__(self, flags=Qt.Widget)
        
        self.setWindowTitle("새로 추가된 Pid 찾기")
        self.setFixedWidth(640)
        self.setFixedHeight(480)
        
        # 베이스 레이아웃
        layout_base = QBoxLayout(QBoxLayout.TopToBottom, self)
        self.setLayout(layout_base)
        
        # 결과 출력을 QListView로 한다.
        grp_QListView = QGroupBox("결과 출력")
        self.listView = QListView(self)
        layout = QBoxLayout(QBoxLayout.TopToBottom)
        layout.addWidget(self.listView)
        grp_QListView.setLayout(layout)
        
        
        
        # 입력을 QLineEdits 2개로 받는다.
        grp_QLineEdits = QGroupBox("URL 입력")
        self.origin_process = QLineEdit()
        self.changed_process = QLineEdit()

        layout = QBoxLayout(QBoxLayout.TopToBottom)
        layout.addWidget(self.origin_process)
        layout.addWidget(self.changed_process)
        grp_QLineEdits.setLayout(layout)
        
        
        # 확인 버튼 누르면 QListView에 결과를 표시한다.
        self.confirm_btn = QPushButton("확인")

        layout_base.addWidget(grp_QListView)
        layout_base.addWidget(grp_QLineEdits)
        layout_base.addWidget(self.confirm_btn)

        self.init_signals()
        
    def init_signals(self):
        self.confirm_btn.clicked.connect(self.on_click)
  
    @pyqtSlot()
    def on_click(self):
        inputedOrigin = self.origin_process.text()
        inputedChanged = self.changed_process.text()
        self.itemModel = QStandardItemModel()
        self.itemModel.appendRow(QStandardItem(inputedOrigin))
        self.itemModel.appendRow(QStandardItem(inputedChanged))
        self.listView.setModel(self.itemModel)
        