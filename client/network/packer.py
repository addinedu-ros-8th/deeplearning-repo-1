# packer.py
import struct


def pack_data(command, pw=None, name=None, height=None, weight=None, data=None, content=None, image_data=None, joint=None, angle=None):
        packed_data = b''

        # 명령어 패킹 (길이 + 데이터)
        packed_data += struct.pack('I', len(command)) + command.encode('utf-8')

        def pack_string(value):
            if value is not None:
                encoded = value.encode('utf-8')
                return struct.pack('I', len(encoded)) + encoded
            return struct.pack('I', 0)

        # 문자열 패킹
        packed_data += pack_string(pw)
        packed_data += pack_string(name)
        packed_data += pack_string(str(height) if height is not None else None)
        packed_data += pack_string(str(weight) if weight is not None else None)
        packed_data += pack_string(data)
        packed_data += pack_string(content)

        # 이미지 데이터 패킹
        if image_data is not None:
            packed_data += struct.pack('I', len(image_data)) + image_data
        else:
            packed_data += struct.pack('I', 0)

        # joint 리스트 패킹
        if joint is not None:
            packed_data += struct.pack('I', len(joint))
            for j in joint:
                packed_data += struct.pack('I', j)
        else:
            packed_data += struct.pack('I', 0)

        # ✅ angle 패킹 (람다 → 문자열 변환)
        if angle is not None:
            if callable(angle):  
                angle_str = f"lambda idx: {angle(0)}"  # 실행 가능한 문자열로 변환
            else:
                angle_str = str(angle)
            packed_data += pack_string(angle_str)
        else:
            packed_data += struct.pack('I', 0)
        
        return packed_data