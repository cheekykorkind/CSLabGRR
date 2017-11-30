#-*- coding: utf-8 -*-
import sys
import re
import os, io
import math
from collections import Counter
import time
import itertools

'''
start함수
파일 1개에 대해서 논문 플로우차트 내용대로 구현함.
1. PE파일여부 판단하기.(MZ시그니쳐 확인)
2. IMAGE_SCN_MEM_WRITE의 값이 0x80이상인지 판단하기.
	1) 복수의 IMAGE_SECTION_HEADER의 offset 파악하기.
	2) 위의 offset으로 Characteristics 판정하기.
	3) WRITE인 Characteristics은 offset 보존하기.
	4) WRITE인 진입점 섹션의 offset 찾기
	5) WRITE인 진입점 섹션의 offset에서 118byte 만큼 엔트로피 구해서 6.85이상이면 파일명과 경로 기록하기.
	
startReadAll함수
의문 : 모든 바이트를 읽어서 엔트로피 값 테스트한 결과 패킹됬다는 샘플이 6.85에 이르지 못하고 있다. 샘플이 문제가 있거나 알고리즘에 문제가 있는거 같다.
	2f4c2e708a955756612d2fa96640547e의 전체 엔트로피  : 3.9536290145622845
	66ed25a173f6caf0a35f8c96e1ec7113의 전체 엔트로피 : 3.9813259473585294
	154093269f2197d7cfb6a88fb37e3d97의 전체 엔트로피 : 3.9813706429418505
	e5e91eb30de08cbe896ffa86d3fdb717의 전체 엔트로피 : 3.6462087259016687
	DB Browser for SQLite.exe의 전체 엔트로피 : 3.5700363223190075
'''

class PackingTest():
	def __init__(self):
		print('This is PackingTest.');
		self.packingInfo = {'entropies': 0, 'packedFile': ''};
		
	
	# 판단시작
	def start(self, fileList, pbar, timerCounter):
		packingInfoList = [];
		currentLoopCounter = 0;		
		
		for file in fileList:
			currentLoopCounter += 1;
		
			fh = open(file, 'rb');
			if not self.checkMZSignature(fh): fh.close(); continue;	# PE파일이 아니면 종료
			
			IMAGE_DOS_HEADER_offset = 0;
			IMAGE_NT_HEADERS_offset = self.getIMAGE_NT_HEADERS_offset(fh);
			entryPointOffsets = self.getEntryPointOffset(fh, IMAGE_NT_HEADERS_offset);
			if entryPointOffsets == 0: fh.close(); continue;	# WRITE 권한이 있는 섹션이 없으므로 종료
			
			entropy = self.getEntropys(fh, entryPointOffsets); 

			packingInfo = {'entropies': 0, 'packedFile': ''};
			packingInfo['entropies'] = entropy;
			packingInfo['packedFile'] = file;
			
			packingInfoList.append(packingInfo);
				
			timerCounter = 100 * currentLoopCounter / len(fileList);
			pbar.setValue(timerCounter);
			
			fh.close();  # 파일 닫기

		return packingInfoList; 
	
	# 개발 단계에서 엔트로피 테스트용이다.
	def startReadAll(self, fileList, pbar, timerCounter):

		packingInfoList = [];
		currentLoopCounter = 0;

		for file in fileList:
			currentLoopCounter += 1;
		
			fh = open(file, 'rb');
			packingInfo = {'entropies': 0, 'packedFile': ''};
			packingInfo['entropies'] = self.readAll(fh);
			packingInfo['packedFile'] = 'x';
			packingInfoList.append(packingInfo);
			
			timerCounter = 100 * currentLoopCounter / len(fileList);
			pbar.setValue(timerCounter);
			
		fh.close();  # 파일 닫기
		
		return packingInfoList; 
		
	# MZ signature를 확인해서 PE파일인지 확인한다.
	def checkMZSignature(self, fh):
		fh.seek(0);
		if fh.read(2).hex() == '4d5a':
			print('MZ 확인.');
			return True;
		else:
			print('MZ 없음.');
			return False;
			
	# IMAGE_NT_HEADERS의 offset을 구한다.
	def getIMAGE_NT_HEADERS_offset(self, fh):	
		fh.seek(60);
		return self.getBytesStringValue(4, fh.read(4));
	
	# IMAGE_FILE_HEADER에서 IMAGE_SECTION_HEADER의 총 개수를 구한다.
	def getSectionHeadersNumber(self, fh):
		fh.seek(self.getIMAGE_NT_HEADERS_offset(fh)+6);
		return self.getBytesStringValue(2, fh.read(2));
	
	# 첫번째 IMAGE_NT_HEADERS의 offset을 찾는다.
	def getIMAGE_SECTION_HEADER_offset(self, fh, IMAGE_NT_HEADER_offset):
		sizeOfOptionalHeaderOffset = IMAGE_NT_HEADER_offset+20;
		fh.seek(sizeOfOptionalHeaderOffset);
		sizeOfOptionalHeader = self.getBytesStringValue(2, fh.read(2));
		first = IMAGE_NT_HEADER_offset+24+sizeOfOptionalHeader;
		return first;
		
	# _IMAGE_SECTION_HEADER의  Characteristics 값을 얻어옴.	
	def getCharacteristics(self, fh, IMAGE_SECTION_HEADER_offset):
		IMAGE_SCN_MEM_WRITE_offset = IMAGE_SECTION_HEADER_offset + 36 + 3;
		fh.seek(IMAGE_SCN_MEM_WRITE_offset);
		return self.getBytesStringValue(1, fh.read(1));

	# IMAGE_SCN_MEM_WRITE의 값이 존재하는 offset을 모은 리스트를 반환한다.
	def getEntryPointOffset(self, fh, IMAGE_NT_HEADERS_offset):
		_IMAGE_SECTION_HEADER_offsets = [];
		
		initialOffset = self.getIMAGE_SECTION_HEADER_offset(fh, IMAGE_NT_HEADERS_offset);
		i = 0;
		sectionsCounter = self.getSectionHeadersNumber(fh);
		hex80 = int('0x80', 16);
		
		while i < sectionsCounter:
			if self.getCharacteristics(fh, initialOffset) >= hex80:
				_IMAGE_SECTION_HEADER_offsets.append(initialOffset + 20);
				print('WRITE 있다.');
			else:
				print('WRITE 없다.');
			initialOffset += 40;
			i += 1;
			
		return _IMAGE_SECTION_HEADER_offsets;
	
	# Characteristics가 WRITE인 SECTION의 offset에서 118 byte만큼의 엔트로피값들을 구한다.
	def getEntropys(self, fh, entryPointOffsets):
		bytesStr = "";
		entropy = 0;
		
		for i in entryPointOffsets:
			fh.seek(i);
			
			whileCouter = 0;
			while whileCouter < 118:
				whileCouter += 1;
				bytesStr += fh.read(1).hex();
				
			p, lns = Counter(bytesStr), float(len(bytesStr));
			entropy = -sum( count/lns * math.log(count/lns, 2) for count in p.values());
			if entropy >= 6.85:
				return entropy;

		return entropy;

	def readAll(self, fh):
		bytesStr = "";
		readStr = "";
		
		fh.seek(0);

		while True:
			readStr = fh.read().hex();
			readStrLen = len(readStr);
			if readStrLen == 0: break;
			bytesStr += readStr; 
			
		p, lns = Counter(bytesStr), float(len(bytesStr));
		entropy = -sum( count/lns * math.log(count/lns, 2) for count in p.values());

		return entropy;
	
	# open(rb)의 결과인 bytes 타입의 값을 Little endian -> Big endian으로 바꾸고 hex String으로 바꾼다. 
	def getBytesStringValue(self, bytesStrLength, bytesStr):
		if bytesStrLength == 1:
			hexStr = bytesStr.hex();
			return int(hexStr, 16);
		elif bytesStrLength == 2:
			hexStr = bytesStr.hex();
			reverseHexStr = hexStr[2:4] + hexStr[0:2];
			return int(reverseHexStr, 16);
		elif bytesStrLength == 4:
			hexStr = bytesStr.hex();
			reverseHexStr = hexStr[6:8] + hexStr[4:6] + hexStr[2:4] + hexStr[0:2];
			return int(reverseHexStr, 16);


# 	# 판단시작
# 	def start(self, fileList, pbar, timerCounter):
# 		packingInfoList = [];
# 		currentLoopCounter = 0;		
# 		
# 		for file in fileList:
# 			currentLoopCounter += 1;
# 		
# 			fh = open(file, 'rb');
# 			if not self.checkMZSignature(fh): fh.close(); pbar.setValue(100); return [];	# PE파일이 아니면 종료
# 			
# 			IMAGE_DOS_HEADER_offset = 0;
# 			IMAGE_NT_HEADERS_offset = self.getIMAGE_NT_HEADERS_offset(fh);
# 			entryPointOffsets = self.getEntryPointOffset(fh, IMAGE_NT_HEADERS_offset);
# 			if entryPointOffsets == 0: fh.close(); pbar.setValue(100); return [];	# WRITE 권한이 있는 섹션이 없으므로 종료
# 			
# 			entropy = self.getEntropys(fh, entryPointOffsets); 
# 			if entropy >= 6.85:
# 				packingInfo = {'entropies': 0, 'packedFile': ''};
# 				packingInfo['entropies'] = entropy;
# 				packingInfo['packedFile'] = file;
# 			else:
# 				packingInfo = {'entropies': 0, 'packedFile': ''};
# 				packingInfo['entropies'] = entropy;
# 				packingInfo['packedFile'] = 'x';
# 			
# 			packingInfoList.append(packingInfo);
# 				
# 			timerCounter = 100 * currentLoopCounter / len(fileList);
# 			pbar.setValue(timerCounter);
# 			
# 			fh.close();  # 파일 닫기
# 
# 		return packingInfoList; 	