#-*- coding: utf-8 -*-
'''
1. 테스트 명 : 윈도우에서 GRR main에 SFTP로 파일전송하기
    1) GRR main에 comeHere라는 디렉토리를 생성.
    2) 아래 코드를 작성(put 함수가 핵심이다.)후 실행
    
2. 결과 : PuTTY에서 ls 명령어로 readMe.txt의 생성을 확인하였다.

부록 : 아이피 주소, 포트번호, 리눅스 아이디, 리눅스 비밀번호는 공개하지 않도록 주의.
'''

import paramiko;

if __name__ == '__main__':
    transport = paramiko.Transport(('아이피주소', 포트번호));
    transport.connect(username='리눅스 아이디', password='리눅스 비밀번호');
    sftp = paramiko.SFTPClient.from_transport(transport);
    
    uploadPath = '/home/cslab/comeHere/readMe.txt';
    localpath = 'E:\\pythonWorkspace\\SQLiteTest\\readMe.txt';
    
    sftp.put(localpath, uploadPath);
    
    sftp.close();
    transport.close();
    

# 리눅스 명령어 여러개는 && 로 잇는다.
#     ssh=paramiko.SSHClient();
#     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy());
#     ssh.connect('아이피주소', 포트번호, '리눅스 아이디', '리눅스 비밀번호');
#     stdin, stdout, stderr = ssh.exec_command('cd comeHere && ls -al');
#     print stdout.readlines();
#     ssh.close();

