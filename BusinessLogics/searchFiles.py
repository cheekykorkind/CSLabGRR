#-*- coding: utf-8 -*-
'''
1. 테스트 명 : 폴더 순회하고 파일만 출력하기. travelingFolders함수 테스트.
    1) 기준이 될 경로 지정.
    2) os.listdir 함수는 현재 폴더의 자식 폴더 or 파일이름을 전부 가져온다.
    3) 파일인지 체크한다. isFile함수 사용
    3-1) 파일이면 파일 이름을 출력한다.
    3-2) 파일이 아니면 폴더이므로 travelingFolders함수를 다시 실행한다.
    
2. 결과 : 성공
    data3.txt
    data2.txt
    data1.txt
    data6.txt
    data5.txt
'''
import sqlite3
import sys
import re
import os
from pathlib import Path

class SearchFiles():
    def __init__(self):
        self.startDir = 'E:\\pythonWorkspace\\fileSearchTest\\travelTest\\';
                
    def start(self):
        # 절대 경로는 본인 시스템에 맞게 수정한다. 
        dirname = 'E:\\pythonWorkspace\\fileSearchTest\\testDatas';
        filenames = os.listdir(dirname)
        for filename in filenames:
            full_filename = os.path.join(dirname, filename)
            fOpen = open(full_filename, 'rb');
            print (full_filename+" : "),
            while True:
                s = fOpen.read(1);
                if s == '': break;
                thisInt = int(ord(s));
                print ('%02X' % thisInt),;  # 1바이트씩 출력
            print ('');
            fOpen.close();  # 파일 닫기
        input('Press enter if you want to turn off this.');    
    
    
    # 자식 디렉토리가 없다 = leaf 파일이거나 디렉토리 이다. 이 함수 실행하면 모든 파일의 대한 path가 나온다. 이걸 PackintTest.py에 돌리면 된다. 
    def travelingFolders(self, dirnames):
        pathResult = [];
        childDirs = os.listdir(dirnames);
    
        for child in childDirs:
            currentPath = os.path.join(dirnames, child);
            pathObj = Path(currentPath);
                    
            if pathObj.is_dir() and pathObj.exists():
                pathResult = pathResult + self.travelingFolders(currentPath);
            elif pathObj.is_file():
                pathResult.append(currentPath);

        return pathResult;
     
               
#     def isLeafDirectory(self, paths, childDirs):
# #         my_file = Path("/path/to/file")
#         result = True;
#         while True:
#             currentLocation = childDirs.pop();
#             if len(childDirs) == 0: break;
#             if Path(os.path.join(paths, currentLocation)).is_dir():
#                 result = False; 
#         return result;
             
    
#     if __name__ == '__main__':
#         startDir = 'E:\\pythonWorkspace\\fileSearchTest\\travelTest\\';
#         travelingFolders(startDir);