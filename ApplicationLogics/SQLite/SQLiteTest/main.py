#-*- coding: utf-8 -*-
'''
1. 테스트 명 : SQlite 파일을 읽고 정규표현식으로 일치하는지 확인하기
    1) SQLite 파일을 open.
    2) 정규표현식을 준비함.
    3) SQLite 파일을 읽은 후 비교한다.
    
2. 결과 : 정규표현식과 일치함. 
    789cd4bc79
'''
import sqlite3
import sys
import re
import os

if __name__ == '__main__':
    conn = sqlite3.connect('000add8b760012432e8b51f4a021c2bec5766bf26c2954ee6a80f22cd4afbab9.sqlite');
     
    p = re.compile('789cd4bc79');
     
    cursor = conn.execute("SELECT value  from tbl where timestamp = 0");
    for row in cursor:
        subject = str(str(row[0]).encode('hex'));
#         print "str(row[0]).encode('hex') = " , str(row[0]).encode('hex'), "\n"
    conn.close();
 
    result = p.match(subject); 
    print result.group()

#     FH = open('readMe.txt', 'rb');
#     while True:
#         s = FH.read(1);
#         if s == '': break;
#         thisInt = int(ord(s));
#         thisByte = ord(s);
#         print '%02X' % thisInt,;  # 1바이트씩 출력
#     FH.close();  # 파일 닫기   