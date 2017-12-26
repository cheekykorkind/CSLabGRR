# coding: utf-8

import math
from collections import Counter

'''
start함수
파일 1개에 대해서 논문 플로우차트 내용대로 구현함.
1. MZ 시그니쳐를 가지고 있는가?
2. 진입점 색션을 찾는다.
	1) address of entry point(RVA)가 속한 section구하기
		(1) IMAGE_SECTION_HEADER의 RVA 항목값을 구한다.
		(2) IMAGE_SECTION_HEADER의 Virtual Size 항목값을 구한다.
		(3) IMAGE_SECTION_HEADER의 RVA 항목값 <= address of entry point(RVA) < IMAGE_SECTION_HEADER의 Virtual Size 항목값
		(loop) 모든 IMAGE_SECTION_HEADER에서 위의 (1)~(3)을 반복한다.
3. 진입점 색션이 write 속성인가?
	1) IMAGE_SECTION_HEADER의 Characteristics attribute의 IMAGE_SCN_MEM_WRITE를 찾는다.
	2) IMAGE_SCN_MEM_WRITE가 0x80이상인지 판단하기.
4. write 속성이면, 진입점 색션의 entropy를 계산한다.
5. entropy가 6.85이상이면 패킹이라고 판단한다.

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
			if not self.checkMZSignature(fh): fh.close(); currentLoopCounter += 1; continue;	# MZ 시그니쳐를 가지고 있는가? 아니면 종료
			
			IMAGE_DOS_HEADER_offset = 0;
			IMAGE_NT_HEADERS_offset = self.getIMAGE_NT_HEADERS_offset(fh);
			IMAGE_OPTIONAL_HEADER_offset = IMAGE_NT_HEADERS_offset + 24;
			addressOfEntryPoint = self.getAddressOfEntryPoint(fh, IMAGE_OPTIONAL_HEADER_offset);
			
			entryPointSectionOffset = self.getEntryPointSection(fh, IMAGE_NT_HEADERS_offset, addressOfEntryPoint);	# 진입점 색션의 offset을 찾는다.
			
			if not self.hasWriteAttribute(fh, entryPointSectionOffset): fh.close(); currentLoopCounter += 1; continue;	# 진입점 색션이 write 속성인가? 아니면 종료
			
			entropy = self.getEntropy(fh, entryPointSectionOffset); 	# write 속성이면, 진입점 색션의 entropy를 계산한다.
			if entropy >= 6.85:
				packingInfo = {'entropies': 0, 'packedFile': ''};
				packingInfo['entropies'] = entropy;
				packingInfo['packedFile'] = file;
			else:
				packingInfo = {'entropies': 0, 'packedFile': ''};
				packingInfo['entropies'] = entropy;
				packingInfo['packedFile'] = file;	# 디버깅용
# 				packingInfo['packedFile'] = 'x';	# release용 
			
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
		return self.getBytesIntValue(4, fh.read(4));
	
	# IMAGE_FILE_HEADER에서 IMAGE_SECTION_HEADER의 총 개수를 구한다.
	def getSectionHeadersNumber(self, fh):
		fh.seek(self.getIMAGE_NT_HEADERS_offset(fh)+6);
		return self.getBytesIntValue(2, fh.read(2));
	
	# 첫번째 IMAGE_NT_HEADERS의 offset을 찾는다.
	def getInitialIMAGE_SECTION_HEADER_offset(self, fh, IMAGE_NT_HEADER_offset):
		sizeOfOptionalHeaderOffset = IMAGE_NT_HEADER_offset+20;
		fh.seek(sizeOfOptionalHeaderOffset);
		sizeOfOptionalHeader = self.getBytesIntValue(2, fh.read(2));
		first = IMAGE_NT_HEADER_offset+24+sizeOfOptionalHeader;
		return first;
		
	# _IMAGE_SECTION_HEADER의  Characteristics 값을 얻어옴.	
	def getCharacteristics(self, fh, IMAGE_SECTION_HEADER_offset):
		IMAGE_SCN_MEM_WRITE_offset = IMAGE_SECTION_HEADER_offset + 36 + 3;
		fh.seek(IMAGE_SCN_MEM_WRITE_offset);
		return self.getBytesIntValue(1, fh.read(1));

	# 진입점 색션을 찾는다.
	def getEntryPointSection(self, fh, IMAGE_NT_HEADERS_offset, addressOfEntryPoint):
		currentOffset = self.getInitialIMAGE_SECTION_HEADER_offset(fh, IMAGE_NT_HEADERS_offset);	# 구 getInitialIMAGE_SECTION_HEADER_offset()를 이름만 바꿔서 사용.
		i = 0;
		
		sectionsCounter = self.getSectionHeadersNumber(fh);	#	구 함수 그대로 사용

		while(i < sectionsCounter):
			rva = self.getRVAAttibute(fh, currentOffset);
			virtualSize = self.getVirtualSize(fh, currentOffset);

			if(rva <= addressOfEntryPoint and addressOfEntryPoint < rva + virtualSize):
				break;
			else:
				currentOffset += 40;
				i += 1;
		return currentOffset;
	
	# IMAGE_SECTION_HEADER에서 RVA attribute를 구한다.
	def getRVAAttibute(self, fh, IMAGE_SECTION_HEADER_offset):
		fh.seek(IMAGE_SECTION_HEADER_offset + 12);
		return self.getBytesIntValue(4, fh.read(4));
		
	# IMAGE_SECTION_HEADER에서 virtual size attribute를 구한다.
	def getVirtualSize(self, fh, IMAGE_SECTION_HEADER_offset):
		fh.seek(IMAGE_SECTION_HEADER_offset+8);
		return self.getBytesIntValue(4, fh.read(4));
		
	# IMAGE_OPTIONAL_HEADER에서 addressOfEntryPoint를 구한다.
	def getAddressOfEntryPoint(self, fh, IMAGE_OPTIONAL_HEADER_offset):
		fh.seek(IMAGE_OPTIONAL_HEADER_offset+16);
		return self.getBytesIntValue(4, fh.read(4)); 
	
	# 진입점 색션이 write 속성인가?
	def hasWriteAttribute(self, fh, entryPointSectionOffset):
		hex80 = int('0x80', 16);
		if self.getCharacteristics(fh, entryPointSectionOffset) >= hex80:
			print('WRITE 있다.');
			return True;
		else:
			print('WRITE 없다.');
			return False;
	
	# write 속성이면, 진입점 색션의 entropy를 계산한다.
	def getEntropy(self, fh, entryPointSectionOffset):
		bytesStr = "";
		readStr = "";
		entropy = 0;
		
		pointerToRawData = entryPointSectionOffset + 20; # 진입점 색션의 시작 file offset
		sizeOfRawData = entryPointSectionOffset + 16;	# 진입점 색션의 size를 담은 file offset
		
		fh.seek(pointerToRawData);
		startOffset = self.getBytesIntValue(4, fh.read(4));
		
		fh.seek(sizeOfRawData);
		sectionSize = self.getBytesIntValue(4, fh.read(4));

		fh.seek(startOffset);
		readStr = fh.read(sectionSize);
		readStrLen = len(readStr);
		
		for i in range(readStrLen):
			bytesStr += chr(readStr[i]);
			
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
			readStr = fh.read();
			readStrLen = len(readStr);
			if readStrLen == 0: break;
			
			for i in range(readStrLen):
				bytesStr += chr(readStr[i]);

		p, lns = Counter(bytesStr), float(len(bytesStr));
		entropy = -sum( count/lns * math.log(count/lns, 2) for count in p.values());

		return entropy;
	
	# open(rb)의 결과인 bytes 타입의 값을 Little endian -> Big endian으로 바꾸고  DEC int로 바꾼다. 
	def getBytesIntValue(self, bytesStrLength, bytesStr):
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
