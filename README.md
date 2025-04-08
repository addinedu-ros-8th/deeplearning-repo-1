# deeplearning-repo-1
DL 프로젝트 1조 저장소. 팀 CHICAGO
<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/addinedu-ros-8th/deeplearning-repo-1">
    <img src="https://github.com/addinedu-ros-8th/deeplearning-repo-1/blob/main/Front.png" alt="Logo" width="500px">
  </a>

  <h3 align="center">피트니스 AI 에이전트(Fitness AI Agent)</h3>

  <p align="center">
    <a href="https://docs.google.com/presentation/d/1iNOuPEVw5FUgLmUJqL00OPBQSc4z1UGs">Presentation</a>
  </p>
</p>

<hr>



<!-- ABOUT THE PROJECT -->
## Preview
AI 기반 스마트 피트니스 트레이닝 시스템 
- **실시간 교정 피드백** : 인건비 절감과 동시에 운동 효과 및 운영 효율성 향상 
- **운동 자동 분류 및 반복 횟수 카운팅** : 수동 입력 없이 완전한 자동 피트니스 기록 시스템 구현
- **맞춤형 운동 가이드 제공 가능성** : 사용자 데이터를 기반으로 추후 운동 난이도 추천 및 진행률 시각화 등 확장 가능


![Image](https://github.com/user-attachments/assets/fc12cd22-ef3a-408d-b2a1-71b10ff9d416)

<br>

| position | name | job |
|:-----:|------|-----|
| leader | 황한문 |  Hand gesture 반응형 UI, 운동 모델 기능 구현, GUI 설계|   
| worker | 남상기 |  서버 구축 및 연동 |   
| worker | 신동철 |  운동 판별, 자세 feedback, 가이드라인 |    
| worker | 박세린 |  GUI 구현 |    

Project Period: 2025.03.14~2025.04.08

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

#### pip requirements
```bash
    pip install pyqt5
    pip install opencv-headless 
    pip install mediapipe
    pip install numpy
    pip install gTTS
    pip install pydub
    pip install tensorflow
    pip install mysql
    pip install matplotlib
```
## Deep Learning 
### Data set 

<img src="https://github.com/user-attachments/assets/319174e8-532d-40fd-819d-b4e536d2ff55" width="500">
<br />

- **스쿼트** : 26개
- **숄더 프레스** : 11개
- **니업** : 14개
- **런지** : 18개
### Model Layer 

<img src="https://github.com/user-attachments/assets/a6d335ef-159e-4331-a0dd-6a4dfdb4d79b" width="500">
<br />

- **epochs** : 20
- **batch_size** : 100
- **sequence** : 20, 30
- **Train,Valid** : 80%, 20%
### Evaluation 
#### Sequence size 
- Sequence size 20
<table>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/f87df427-a4a4-4249-9fb8-4493216c2d62" width="300"></td>
    <td><img src="https://github.com/user-attachments/assets/144eaa57-c065-4896-bd38-8ee5a2b086ee" width="300"></td>
  </tr>
  <tr>
    <td align="center">Confusion Matrix</td>
    <td align="center">정확도: 77%</td>
  </tr>
</table>
- Sequence size 30
<table>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/6f33ed1e-d01f-4cb7-afaf-a82e28d7b84d" width="300"></td>
    <td><img src="https://github.com/user-attachments/assets/6f4c5e8b-9ef7-41e1-b692-21a3dcb4406a" width="300"></td>
  </tr>
  <tr>
    <td align="center">Confusion Matrix</td>
    <td align="center">정확도: 86%</td>
  </tr>
</table>

- Training History
<br />
<img src="https://github.com/user-attachments/assets/cfd90b57-cc5b-41eb-b3b3-fbecb73dfe15" width="500">

- result
<br />
<img src="https://github.com/user-attachments/assets/eb6fbcc9-7537-4757-beca-b1ba8d499f8d" width="500">

## 주요 기능 
### Login 
![Image](https://github.com/user-attachments/assets/fab18721-b4bd-4628-a3ac-186867eefb38)
### Hand gesture UI 

#### Lookup - 티어별 운동들 살펴보기   
![Image](https://github.com/user-attachments/assets/4879d38c-d6cb-4a4c-a3a6-226bc995d4b0)
#### Hand gesture (손가락인식)
![Image](https://github.com/user-attachments/assets/5ce51d23-7b70-46bd-af8f-2a0e75ded9b8)

### Workout - drawline, counting, tts 
#### Break time
![Image](https://github.com/user-attachments/assets/29590237-c99e-40eb-aafd-a7890b883574)
#### Time over 
![Image](https://github.com/user-attachments/assets/4f285284-2fcd-43e0-b30a-1e0114c029d6)



## 설계
### 시나리오
#### Sequence Diagram
![Image](https://github.com/user-attachments/assets/af8de992-43fa-4db0-aee4-966a16b259f4)

### Workout list
|  Tier  |  이름  | 설명 | Tier  |  이름  | 설명 
|:--------:|--------|------|------|------|------| 
| Bronze | Knee-up |<img src="https://github.com/user-attachments/assets/2fb58870-ff32-45e9-8952-aeaf15adc516" width="230" height="200">|   silver |  Push-up | <img src="https://github.com/user-attachments/assets/f3536570-02d8-4dcb-9117-cc20586604d3" width="250" height="200">|
| Bronze | Shoulder-press | <img src="https://github.com/user-attachments/assets/e1858e72-ae25-48f2-b574-f3ac9a97defd" width="230" height="200">| silver | Bridge| <img src="https://github.com/user-attachments/assets/9c3e0b79-951d-47f4-8413-c83d87ef68ac" width="250" height="200">|
| Bronze | Squat |<img src="https://github.com/user-attachments/assets/491558c9-faaa-4b01-8d36-5a93c5eb2b85" width="230" height="200">| silver| Standing Bicycle |<img src="https://github.com/user-attachments/assets/67b59edf-f230-487e-92e9-16ef001b4ae0" width="250" height="200">|
| Bronze | Front-lunge |<img src="https://github.com/user-attachments/assets/e043a262-e350-4472-a08f-83c30f68440e" width="230" height="200">| silver| Side lunge |<img src="https://github.com/user-attachments/assets/e127fadd-b4bc-4498-b52d-681b0251f387" width="250" height="200">| 



### Architecture  
#### 1) System Atchitecture
![Image](https://github.com/user-attachments/assets/13a78c71-6e38-424f-a4a7-bb9ba25d9b86)
#### 2) ERD 
![Image](https://github.com/user-attachments/assets/fffa8ef7-b725-47d5-8c10-b99cf20ea940)


 

