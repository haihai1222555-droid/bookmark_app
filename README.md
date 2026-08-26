# 나만의 북마크

웹에서 찾은 주소에 내가 기억하기 쉬운 제목을 붙여 저장하고, 제목의 일부로 다시 찾는 간단한 개인 북마크 서비스입니다.

이 프로젝트는 HTML/CSS/JavaScript/Python/Flask/MongoDB를 처음 배우는 2명이 이해할 수 있도록 파일 수와 코드 구조를 작게 유지했습니다.

## 사용 기술

- 화면: HTML, CSS, Bootstrap, JavaScript, jQuery, AJAX
- 서버: Python, Flask, Jinja2
- 데이터베이스: MongoDB, PyMongo
- 로그인 유지: Flask session

로그인 방식은 JWT 대신 Flask session을 선택했습니다. 로그인 성공 시 사용자의 ID만 서버 세션 쿠키에 저장합니다. 이 프로젝트 규모에서는 코드를 더 짧고 쉽게 읽을 수 있기 때문입니다.

## 파일 구조

```text
fail/
├─ app.py
├─ requirements.txt
├─ .env.example
├─ templates/
│  ├─ login.html
│  ├─ signup.html
│  └─ main.html
└─ static/
   ├─ style.css
   └─ main.js
```

## 실행 방법

### 1. 프로젝트 폴더 열기

VS Code에서 이 폴더를 엽니다. 터미널에서 아래 명령을 실행합니다.

```powershell
cd C:\Users\Leo\Desktop\fail
```

### 2. 가상환경 만들기

```powershell
python -m venv .venv
```

### 3. 가상환경 활성화

PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

명령 프롬프트(cmd):

```bat
.venv\Scripts\activate.bat
```

PowerShell 실행 정책 오류가 나면 명령 프롬프트에서 활성화 명령을 실행해도 됩니다.

### 4. 필요한 패키지 설치

```powershell
pip install -r requirements.txt
```

### 5. MongoDB 준비

로컬 MongoDB를 사용한다면 MongoDB Community Server를 설치하고 실행합니다. 기본 주소는 아래와 같습니다.

```text
mongodb://localhost:27017/
```

MongoDB Atlas를 사용한다면 Atlas에서 받은 연결 주소를 사용할 수 있습니다.

### 6. 환경변수 파일 만들기

`.env.example` 파일을 복사해서 이름을 `.env`로 바꿉니다.

```powershell
Copy-Item .env.example .env
```

`.env`의 내용을 환경에 맞게 수정합니다.

```env
MONGO_URI=mongodb://localhost:27017/
DB_NAME=my_bookmark
SECRET_KEY=나만알수있는랜덤문자열
```

실제 비밀값이 있는 `.env` 파일은 Git에 올리지 마세요.

### 7. Flask 실행

```powershell
python app.py
```

브라우저에서 아래 주소로 접속합니다.

```text
http://127.0.0.1:5000
```

## 사용 순서

1. 로그인 화면 아래의 `회원가입` 링크를 누릅니다.
2. ID를 입력하고 `중복 확인`을 누릅니다.
3. PW와 PW 확인을 입력하고 가입합니다.
4. 로그인합니다.
5. `+ 템플릿 추가`를 눌러 제목과 URL을 저장합니다.
6. 제목 앞 화살표를 눌러 주소, 수정, 삭제 버튼을 확인합니다.
7. 검색창에 제목의 일부를 입력해서 검색합니다.

테스트할 때 다음 데이터를 직접 추가해볼 수 있습니다.

| 제목 | URL 예시 |
| --- | --- |
| 요리 칼질 블로그 | https://example.com/cooking |
| 개발 Flask 로그인 참고 | https://flask.palletsprojects.com/ |
| 여행 제주도 맛집 | https://example.com/jeju |

## 구현된 기능

- 회원가입, ID AJAX 중복 확인, 비밀번호 해시 저장
- 로그인 실패 문구와 Flask session 로그인 유지
- 로그인 사용자별 북마크 분리
- Jinja2 서버 사이드 렌더링으로 첫 목록 표시
- AJAX 북마크 생성, 수정, 삭제, 제목 부분 검색
- 북마크 상세 내용 펼치기/접기
- 로그아웃
- 수정과 삭제 시 북마크 ID와 로그인 사용자를 함께 검사

## 미완성 또는 단순하게 만든 부분

- 비밀번호 규칙과 아이디 글자 수 검사는 생략했습니다.
- 수정 화면은 별도 모달 대신 브라우저의 `prompt` 창을 사용합니다.
- 페이지 나누기, 정렬, 즐겨찾기 분류 기능은 없습니다.
- Bootstrap과 jQuery는 CDN을 사용하므로 화면을 정상 표시하려면 인터넷 연결이 필요합니다.
- 실제 배포용 서버 설정과 HTTPS 설정은 포함하지 않았습니다.

## 공부하면 좋은 순서

1. `app.py`의 `login()`, `signup()` 함수로 GET/POST와 세션을 봅니다.
2. `templates/main.html`에서 Jinja2의 `for` 반복문을 봅니다.
3. `app.py`의 `create_bookmark()`에서 MongoDB 저장을 봅니다.
4. `static/main.js`에서 jQuery AJAX가 Flask 주소를 호출하는 방법을 봅니다.
5. `update_bookmark()`, `delete_bookmark()`의 owner 조건으로 사용자 데이터 분리를 봅니다.
6. `search_bookmarks()`에서 제목 부분 검색 방법을 봅니다.

## MongoDB 연결 오류가 나올 때

`MongoDB 연결이 필요합니다` 화면이 나오면 MongoDB 서버가 설치되지 않았거나 꺼진 상태입니다.

MongoDB Community Server를 설치할 때 `Install MongoD as a Service` 옵션을 선택합니다. 설치 후 PowerShell에서 상태를 확인할 수 있습니다.

```powershell
Get-Service MongoDB
```

서비스가 설치되어 있지만 멈춰 있다면 관리자 권한 PowerShell에서 실행합니다.

```powershell
Start-Service MongoDB
```

## Render에 배포하기

이 프로젝트에는 Render 배포 설정인 `render.yaml`과 `.python-version`이 들어 있습니다. `.env`는 비밀번호가 있으므로 GitHub에 올리지 않습니다.

### 1. GitHub 저장소 만들기

GitHub에서 새 저장소를 만들고 이 프로젝트를 올립니다. `.env`, `.venv` 폴더가 올라가지 않았는지 반드시 확인합니다.

### 2. MongoDB Atlas 네트워크 허용

Atlas의 Network Access에서 Render가 접속할 수 있도록 IP를 허용합니다. 처음 배포 확인만 할 때는 `0.0.0.0/0`을 임시로 추가할 수 있습니다. 배포가 끝나면 Render 서비스의 Outbound IP 범위만 허용하는 편이 더 안전합니다.

### 3. Render에서 서비스 만들기

1. Render에 GitHub 계정으로 로그인합니다.
2. `New` → `Blueprint`를 누릅니다.
3. GitHub의 프로젝트 저장소를 선택합니다.
4. `MONGO_URI` 값에는 로컬 `.env`에 사용한 Atlas 연결 문자열을 입력합니다.
5. 배포를 시작합니다.

`render.yaml`이 다음 설정을 자동으로 사용합니다.

- Python Web Service
- 빌드: `pip install -r requirements.txt`
- 실행: `gunicorn app:app`
- 데이터베이스 이름: `my_bookmark`
- HTTPS 세션 쿠키 사용

배포가 완료되면 Render가 `https://...onrender.com` 형태의 주소를 제공합니다.

### 무료 서비스 참고

Render 무료 서비스는 한동안 방문이 없으면 잠들 수 있습니다. 그 다음 첫 접속은 서버가 다시 깨어나는 동안 시간이 조금 걸릴 수 있습니다.
