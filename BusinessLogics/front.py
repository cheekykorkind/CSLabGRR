# coding: utf-8
import sys

from PyQt5.QtWidgets import QWidget, QPushButton, QGroupBox, QAbstractItemView, QBoxLayout, QListView, QFileDialog, QProgressBar  

from PyQt5.QtGui import QStandardItemModel, QStandardItem 

from PyQt5.QtCore import Qt, pyqtSlot, QBasicTimer

from searchFiles import SearchFiles
from PackingTest import PackingTest
import time

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
        layout = QBoxLayout(QBoxLayout.TopToBottom)
        
        self.listView = QListView(self)
        self.listView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        layout.addWidget(self.listView)
        grp_QListView.setLayout(layout)

        # 프로그래스 바 레이아웃
        grp_QProgressBar = QGroupBox("진행도")
        grp_QProgressBar_layout = QBoxLayout(QBoxLayout.TopToBottom)
         
        self.pbar = QProgressBar(self)
 
        grp_QProgressBar_layout.addWidget(self.pbar)
        grp_QProgressBar.setLayout(grp_QProgressBar_layout)
        
        # 확인 버튼 누르면 QListView에 결과를 표시한다.
        self.confirm_btn = QPushButton("확인")

        layout_base.addWidget(grp_QListView)
        layout_base.addWidget(grp_QProgressBar)
        layout_base.addWidget(self.confirm_btn)


        self.progressTimer = QBasicTimer(); # 프로그래스 바에 쓰는 타이머 인스턴스
        self.timerCounter = 1;  # 프로그래스 바 진행상황 표시에 사용할 변수
        
        self._PackingTest = PackingTest();  # 패킹 테스트하는 인스턴스
        
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
        fileListLength = len(fileList);

        # 프로그래스 바 타이머 시작
        self.progressTimer.start(100, self);
         
        if fileListLength == 0: self.pbar.setValue(100); return ;
        
        start_time = time.time()
        
        # 패킹 파일을 검사한다.
        testResult = [];
#         testResult = self._PackingTest.start(fileList, self.pbar, self.timerCounter);
#         testResult = self._PackingTest.startNoEntropyCheck(fileList, self.pbar, self.timerCounter);
        testResult = self._PackingTest.startReadAll(fileList, self.pbar, self.timerCounter);

        
        print("--- %s seconds ---" %(time.time() - start_time))
            
        for i in testResult:
            resultStr = str(i['entropies']) + ' <- ' +  i['packedFile'];
            self.itemModel.appendRow(QStandardItem(resultStr));
             
        self.listView.setModel(self.itemModel);

    # 디렉토리 선택창을 띄우고 선택한 디렉토리의 경로를 반환한다.
    def selectDirectory(self):
        dialog = QFileDialog()
        DirectoryPath = dialog.getExistingDirectory(None, "Select Folder")
        return DirectoryPath;

    # 시간에 따른 프로그래스 바의 진행도를 측정하고 종료시키는 함수이다.    
    def timerEvent(self, e):
        if self.timerCounter >= 100:
            self.progressTimer.stop()
            return

