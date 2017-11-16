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

def readFile():
    # 절대 경로는 본인 시스템에 맞게 수정한다. 
    dirname = 'E:\\pythonWorkspace\\fileSearchTest\\testDatas';
    filenames = os.listdir(dirname)
    for filename in filenames:
        full_filename = os.path.join(dirname, filename)
        fOpen = open(full_filename, 'rb');
        print full_filename+" : ",
        while True:
            s = fOpen.read(1);
            if s == '': break;
            thisInt = int(ord(s));
            print '%02X' % thisInt,;  # 1바이트씩 출력
        print '';
        fOpen.close();  # 파일 닫기
    input('Press enter if you want to turn off this.');    


# 폴더 순회 종료 조건은 폴더가 비었거나 파일만 있을때다.
def travelingFolders(dirnames):
    filenames = os.listdir(dirnames);
    fileCount = len(filenames); # 폴더 안의 폴더와 파일 갯수를 파악하기 위한 변수이다. leaf 폴더를 결정하는데 사용한다.
    
    while len(filenames) != 0:
        tempNode = filenames.pop();
        if isFile(tempNode):
            fileCount = fileCount -1;
            print tempNode;  
        else:
            travelingFolders(os.path.join(dirnames, tempNode));
            

def isFile(files):
    p = re.compile(r"\w+[.]\w+");
    m = p.match(files);
    if m:
        return True;
#         print'Match found: '+m.group()
    else:
        return False;
#         print('No match')

def isEnd(files):
    if len(files) == 0: #빈 폴더이다.
        return True;
    elif isFile(files): # 비지 않았는데 파일이 있다.
        return True; 

if __name__ == '__main__':
    startDir = 'E:\\pythonWorkspace\\fileSearchTest\\travelTest\\';
    travelingFolders(startDir);