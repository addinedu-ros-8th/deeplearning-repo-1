# packer.py
import struct


def pack_data(command, pw=None, name=None, height=None, weight=None, data=None, content=None, image_data=None):
        packed_data = b''
        
        # 명령어 패킹 (길이 + 데이터)
        packed_data += struct.pack('I', len(command)) + command.encode('utf-8')
        
        # 비밀번호 패킹 (길이 + 데이터)
        if pw is not None:
            packed_data += struct.pack('I', len(pw)) + pw.encode('utf-8')
        else:
            packed_data += struct.pack('I', 0)
        
        # 이름 패킹 (길이 + 데이터)
        if name is not None:
            packed_data += struct.pack('I', len(name.encode('utf-8'))) + name.encode('utf-8')
        else:
            packed_data += struct.pack('I', 0)
        
        # 키 높이 패킹 (길이 + 데이터)
        if height is not None:
            packed_data += struct.pack('I', len(str(height))) + str(height).encode('utf-8')
        else:
            packed_data += struct.pack('I', 0)
        
        # 몸무게 패킹 (길이 + 데이터)
        if weight is not None:
            packed_data += struct.pack('I', len(str(weight))) + str(weight).encode('utf-8')
        else:
            packed_data += struct.pack('I', 0)
        
        # 데이터 패킹
        if data is not None:
            data_bytes = data.encode('utf-8')
            packed_data += struct.pack('I', len(data_bytes)) + data_bytes
        else:
            packed_data += struct.pack('I', 0)
        
        # 콘텐트 패킹
        if content is not None:
            content_bytes = content.encode('utf-8')
            packed_data += struct.pack('I', len(content_bytes)) + content_bytes
        else:
            packed_data += struct.pack('I', 0)
        
        # 이미지 데이터 패킹 (이미지 파일을 바이너리로 읽어 전달)
        if image_data is not None:
            packed_data += struct.pack('I', len(image_data)) + image_data
        else:
            packed_data += struct.pack('I', 0)

        return packed_data