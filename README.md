## live stream pipe line 
[ Webcam Thread ]\
&emsp; ↓ (프레임 읽기)\
[ MainWindow ]\
&emsp; ↓ (QTimer 주기적 호출)\
[ update_frame() ]\
&emsp; ↓ (프레임을 QLabel로 출력)\
[ displayImage() ]
