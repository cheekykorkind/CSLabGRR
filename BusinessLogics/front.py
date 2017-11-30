# coding: utf-8
import sys

from PyQt5.QtWidgets import QWidget, QPushButton, QGroupBox, QAbstractItemView, QBoxLayout, QListView, QApplication, QFileDialog  

from PyQt5.QtGui import QStandardItemModel, QStandardItem 

from PyQt5.QtCore import Qt, pyqtSlot

from searchFiles import SearchFiles
from PackingTest import PackingTest

class Form(QWidget):
    def __init__(self):
        QWidget.__init__(self, flags=Qt.Widget)
        
        self.setWindowTitle("Packing check")
        self.resize(640, 480)
        
        # 베이스 레이아웃
        layout_base = QBoxLayout(QBoxLayout.TopToBottom, self)
        self.setLayout(layout_base)
        
        # 결과 출력을 QListView로 한다.
        grp_QListView = QGroupBox("결과 출력")
        self.listView = QListView(self)

        self.listView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout = QBoxLayout(QBoxLayout.TopToBottom)
        layout.addWidget(self.listView)
        grp_QListView.setLayout(layout)
        
        # 확인 버튼 누르면 QListView에 결과를 표시한다.
        self.confirm_btn = QPushButton("확인")

        layout_base.addWidget(grp_QListView)
#         layout_base.addWidget(grp_QLineEdits)
        layout_base.addWidget(self.confirm_btn)


        self._PackingTest = PackingTest();
        self.init_signals()
        self.show()
        
    def init_signals(self):
        self.confirm_btn.clicked.connect(self.on_click)
  
    @pyqtSlot()
    def on_click(self):
        DirectoryPath = self.selectDirectory();

        # UI의 X를 눌렀을때 None이 DirectoryPath에 들어가서 에러나기 때문에 추가한다.
        if len(DirectoryPath) == 0: return ;

        self.itemModel = QStandardItemModel();
        fileList = SearchFiles().travelingFolders(DirectoryPath);
        testResult = [];
        
        
        
        # testResult = {'entropies': 0, 'packedFile': ''} 형태이다.    
        for i in fileList:
            tmpResult = self._PackingTest.startReadAll(i);
            testResult.append(self._PackingTest.startReadAll(i));
#             
            resultStr = str(tmpResult['entropies']) + ' <- ' +  tmpResult['packedFile'];
            
            self.itemModel.appendRow(QStandardItem(resultStr));
#             self.itemModel.appendRow(QStandardItem(str(i)));
            
            
        self.listView.setModel(self.itemModel);

    # 디렉토리 선택창을 띄우고 선택한 디렉토리의 경로를 반환한다.
    def selectDirectory(self):
        dialog = QFileDialog()
        DirectoryPath = dialog.getExistingDirectory(None, "Select Folder")
        return DirectoryPath;
