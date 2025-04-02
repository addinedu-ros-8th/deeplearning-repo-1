# deeplearning-repo-1
DL 프로젝트 1조 저장소. 팀 CHICAGO
<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/addinedu-ros-8th/deeplearning-repo-1">
    <img src="https://github.com/addinedu-ros-8th/deeplearning-repo-1/blob/main/FRONT.png" alt="Logo" width="500px">
  </a>

  <h3 align="center">피트니스 AI 에이전트(Fitness AI Agent)</h3>

  <p align="center">
    <a href="">Video Demo</a>\\
    <a href="">Presentation</a>
  </p>
</p>

<hr>



<!-- ABOUT THE PROJECT -->
## Preview
AI 기반 스마트 피트니스 트레이닝 시스템 
- **실시간 교정 피드백** : 인건비 절감과 동시에 운동 효과 및 운영 효율성 향상 
- **운동 자동 분류 및 반복 횟수 카운팅** : 수동 입력 없이 완전한 자동 피트니스 기록 시스템 구현
- **맞춤형 운동 가이드 제공 가능성** : 대규모(e.g. 물류센터 및 창고) -> 소규모(e.g. 마트) 


mp4 - video

<br>

| position | name | job |
|:-----:|------|-----|
| leader | 황한문 |  Hand gesture 반응형 UI, 운동 모델 기능 구현, GUI 설계 |   
| worker | 남상기 |  서버 구축 및 연동, 운동 counting, GUI 구현 |   
| worker | 신동철 |  운동 판별, 자세 feedback, 가이드라인 |    
| worker | 박세린 |  GUI 구현, 운동데이터 수집 |    

## Instructions
### Environment   
- Dev: PyQt/Qt 5 Designer - python
- DB: AWS RDS - MySQL
- Collab: Jira, Confluence and Slack   
- OS: Ubuntu 24.04
### Installation 
```bash 
    git clone https://github.com/addinedu-ros-8th/deeplearning-repo-1.git
    code deeplearning-repo-1
```
#### python env 
```bash 
    mkdir <venv> 
    cd <venv>
    python -m venv <env>
    source ~/<venv>/<env>/bin/activate
```
#### Qt Designer 
- Linux  
```bash 
    sudo apt install qttools5-dev-tools
    sudo apt install qttools5-dev
```
#### PyQt5
- Linux 
```bash 
    pip install pyqt5
    sudo apt-get install pyqt5-dev-tools
```
#### pip requirements
```bash
    pip install opencv-headless 
    pip install mediapipe
    pip install numpy
    pip install gTTS
    pip install pydub
    pip install tensorflow
```



## 설계
### 시나리오
#### 1) Simple Diagram
#### 2) State Diagram 

### Workout list
|  Tier  |  이름  | 설명 | Tier  |  이름  | 설명 
|:--------:|--------|------|------|------|------| 
| Bronze | Knee-up |<img src="https://github.com/user-attachments/assets/2fb58870-ff32-45e9-8952-aeaf15adc516" width="250" height="200">|   silver |  Push-up | <img src="https://github.com/user-attachments/assets/f3536570-02d8-4dcb-9117-cc20586604d3" width="250" height="200">|
| Bronze | Sholder-press | <img src="https://github.com/user-attachments/assets/e1858e72-ae25-48f2-b574-f3ac9a97defd" width="250" height="200">| silver | Bridge| <img src="https://github.com/user-attachments/assets/9c3e0b79-951d-47f4-8413-c83d87ef68ac" width="250" height="200">|
| Bronze | Squat |<img src="https://github.com/user-attachments/assets/491558c9-faaa-4b01-8d36-5a93c5eb2b85" width="250" height="200">| silver| Standing Bicycle |<img src="https://github.com/user-attachments/assets/67b59edf-f230-487e-92e9-16ef001b4ae0" width="250" height="200">|
| Bronze | Front-lunge |<img src="https://github.com/user-attachments/assets/e043a262-e350-4472-a08f-83c30f68440e" width="250" height="200">| silver| Side lunge |<img src="https://github.com/user-attachments/assets/e127fadd-b4bc-4498-b52d-681b0251f387" width="250" height="200">| 

|  Tier  |  이름  | 설명 |
|:--------:|--------|------|
| Gold |Sit-up|<img src="https://github.com/user-attachments/assets/71533531-f640-41a6-a9a8-8a0c02339610" width="250" height="200">|    
| Gold |Side-plank|<img src="https://github.com/user-attachments/assets/d10ed58e-d8c4-468b-b2c6-9f7ae036c877" width="250" height="200">|  
| Gold |One-leg-knee-up|<img src="https://github.com/user-attachments/assets/21235710-f7d0-45aa-8e98-de98786791c0" width="250" height="200">| 
| Gold |V-up|<img src="https://github.com/user-attachments/assets/bd2f1997-ab37-4f33-a336-bcec9089bd99" width="250" height="200">| 


### Architecture  
#### 1) SW
![Image](https://github.com/user-attachments/assets/5796be21-5a7c-438a-b598-ea8193de69ac)
#### 2) HW
![Image](https://github.com/user-attachments/assets/ee48d138-91da-4a27-8f0a-88d739a6a221)
#### 3) ERD 
![Image](https://github.com/user-attachments/assets/fb42019f-67a3-46c5-bd02-2793efa1790e)

## 기능 
### 기능 리스트 
|  기능  | 설명 |
|:--------:|------| 
| Auth  | ID,PW 인증관리 |    
| Counting | 운동 Counting |
| Feedback | 운동 Guide line, 운동 음성/시각 feedback |
| Tier | 티어별 운동 리스트 조회 |      
| Test | score기반의 tier test 기능 |     
| Record | 일/주/월 운동 기록 시각화, |
| Goal | 목표 설정 |

 
## Project Schesule
Project Period: 2025.02.19~2025.02.26
<br >

