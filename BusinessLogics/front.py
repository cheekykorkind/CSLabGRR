# coding: utf-8
import sys
import re
import paramiko

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
        pathList = [];
        packingTestResult = [];
        packingTestResult = self._PackingTest.start(fileList, self.pbar, self.timerCounter);
        
        print("--- %s seconds ---" %(time.time() - start_time));
        
        # paramiko에 적절한 path로 String을 고친다.
        for i in packingTestResult:
            # 파일 이름 얻기
            fullPath = i['packedFile'];
            if fullPath == 'x': continue;   # 패킹 파일이 아니면 'x'가 들어있다. 'x'는 경로가 아니므로 무시한다.
            
            currentToken = re.search('\\\(\w*)', fullPath);
            nextStrIndex = 0;
            
            # 폴더 선택하는 level에 따라서 backslash 개수가 달라진다. 예를 들어 하위 폴더가 2 level있는 폴더를 선택하면 backslash가 하위 경로에 2번 나타난다.
            while(currentToken is not None):
                if(nextStrIndex == 0):
                    nextStrIndex = currentToken.start() + 1;
                    currentToken = re.search('\\\(\w*)', fullPath[nextStrIndex:]);
                    nextStr = fullPath[nextStrIndex:];
                else:
                    nextStrIndex = currentToken.start() + 1;
                    currentToken = re.search('\\\(\w*)', nextStr[nextStrIndex:]);
                    nextStr = nextStr[nextStrIndex:];
                    
            fileName = nextStr; 
#             print(fileName);
             
            # full path 얻기
            fullPath = fullPath.replace('/', '\\').replace('\\', '\\\\'); 
#             print(fullPath);
            
            # GUI에 출력하기
            rowString = str(i['entropies']) + ' <- ' +  fullPath;
            self.itemModel.appendRow(QStandardItem(rowString));
            
            pathInfo = {'fileName': fileName, 'fullPath': fullPath};
            pathList.append(pathInfo);
              
        self.listView.setModel(self.itemModel);
        
        # SFTP를 사용해서 Sever로 파일 전송한다.
        self.transferFilesToSever(pathList);

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
    
    # SFTP를 사용해서 Sever로 파일 전송한다.
    def transferFilesToSever(self, pathList):
        transport = paramiko.Transport(('IP', port));	# IP 및 port 번호 공개하지 않도록 주의
        transport.connect(username='', password='');	# 계정 및 비밀번호 공개하지 않도록 주의
        sftp = paramiko.SFTPClient.from_transport(transport);

        for i in pathList:
            uploadPath = '/경로/'+i['fileName'];	# 경로 공개하지 않도록 주의
            localpath = i['fullPath'];
        
            sftp.put(localpath, uploadPath);
          
        sftp.close();
        transport.close();
