# PDF Analyzer

PDF 파일에서 표와 텍스트를 추출하여 Excel과 텍스트 파일로 변환하는 애플리케이션입니다.

## 주요 기능

1. **현장정보 추출**
   - PDF 파일의 1-5 페이지 또는 지정한 페이지 범위에서 텍스트와 표를 추출
   - 추출된 텍스트는 텍스트 파일(.txt)로 저장
   - 추출된 표는 Excel 파일(.xlsx)로 저장
   - 각 표는 별도의 시트에 저장되며, 페이지 번호와 표 번호로 구분

2. **표 추출**
   - 지정한 페이지 범위에서 표만 추출
   - 추출된 표는 Excel 파일(.xlsx)로 저장
   - 각 표는 별도의 시트에 저장

## 설치 방법

### Windows 설치
1. 필요한 라이브러리 설치:
```bash
pip install streamlit tabula-py pandas PyPDF2
```

2. Java 설치 (tabula-py 사용을 위해 필요):
   - [Java JDK](https://www.oracle.com/java/technologies/downloads/) 다운로드 및 설치
   - 시스템 환경 변수에 Java 경로 추가

### Ubuntu 서버 설치
1. 시스템 업데이트:
```bash
sudo apt update
sudo apt upgrade -y
```

2. Python 및 pip 설치:
```bash
sudo apt install python3 python3-pip python3-venv -y
```

3. Java 설치:
```bash
sudo apt install default-jdk -y
```

4. 프로젝트 디렉토리 생성 및 이동:
```bash
mkdir pdf_extractor
cd pdf_extractor
```

5. 가상환경 생성 및 활성화:
```bash
python3 -m venv venv
source venv/bin/activate
```

6. 필요한 라이브러리 설치:
```bash
pip install streamlit tabula-py pandas PyPDF2
```

7. 애플리케이션 실행:
```bash
# 개발 모드로 실행
streamlit run app.py

# 백그라운드에서 실행 (nohup 사용)
nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 > streamlit.log 2>&1 &

# 실행 중인 프로세스 확인
ps aux | grep streamlit

# 로그 확인
tail -f streamlit.log
```

8. 방화벽 설정 (필요한 경우):
```bash
# UFW 방화벽 사용 시
sudo ufw allow 8501

# iptables 사용 시
sudo iptables -A INPUT -p tcp --dport 8501 -j ACCEPT
```

9. 서비스 등록 (systemd 사용 시):
```bash
# 서비스 파일 생성
sudo nano /etc/systemd/system/pdf-analyzer.service

# 서비스 파일 내용
[Unit]
Description=PDF Analyzer Streamlit App
After=network.target

[Service]
User=your_username
WorkingDirectory=/path/to/pdf_extractor
Environment="PATH=/path/to/pdf_extractor/venv/bin"
ExecStart=/path/to/pdf_extractor/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target

# 서비스 시작
sudo systemctl start pdf-analyzer
sudo systemctl enable pdf-analyzer

# 서비스 상태 확인
sudo systemctl status pdf-analyzer
```

10. 접속 방법:
    - 웹 브라우저에서 `http://서버IP:8501` 접속
    - 예: `http://192.168.1.100:8501`

## 사용 방법

1. PDF 파일 선택:
   - "PDF 파일 선택하기" 버튼을 클릭하여 파일 선택
   - 또는 파일 경로를 직접 입력

2. 페이지 범위 설정:
   - 시작 페이지와 끝 페이지 입력
   - 현장정보 추출 시 페이지 범위를 입력하지 않으면 1-5 페이지 자동 처리

3. 추출 옵션 설정 (표 추출 시):
   - 격자형 표: 표에 선이 있는 경우 선택
   - 스트림 모드: 표에 선이 없는 경우 선택
   - 자동 감지: 표 위치를 자동으로 감지

4. 추출 실행:
   - "현장정보 추출" 버튼: 텍스트와 표를 함께 추출
   - "표 추출하기" 버튼: 표만 추출

5. 결과 다운로드:
   - 추출된 텍스트는 .txt 파일로 다운로드
   - 추출된 표는 .xlsx 파일로 다운로드
   - 파일명은 원본 PDF 파일명을 기반으로 생성
     - 텍스트 파일: [PDF파일명]_text.txt
     - Excel 파일: [PDF파일명]_tables.xlsx

## 주의사항

1. PDF 파일이 손상되지 않았는지 확인
2. Java가 올바르게 설치되어 있는지 확인
3. 표 추출이 실패하는 경우 다른 추출 옵션을 시도
4. 대용량 PDF 파일 처리 시 시간이 다소 소요될 수 있음

## 파일 구조

- `app.py`: 메인 애플리케이션 파일
- `temp/`: 임시 파일 저장 디렉토리 (자동 생성)
- `README.md`: 사용 설명서

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 