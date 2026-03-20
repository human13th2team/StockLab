# 📈 StockLab (주식 자동매매 시스템)

이 프로젝트는 Flask 기반의 주식 데이터 분석 및 자동매매 시스템입니다. 팀원들이 로컬 환경에서 원활하게 개발을 시작할 수 있도록 아래 가이드를 따라주세요.

## 🛠 필수 소프트웨어
- **Python**: 3.8 이상 (3.10 권장)
- **MariaDB / MySQL**: 10.x 이상
- **Git**

## 🚀 로컬 개발 환경 구축 (Quick Start)

### 1. 프로젝트 복제 (Clone)
```bash
git clone <repository_url>
cd StockLab
```

### 2. 가상 환경 생성 및 활성화
**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```
**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. 패키지 설치
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. 환경 변수 설정
`.env.example` 파일을 복사하여 `.env` 파일을 만듭니다.
```bash
cp .env.example .env
```
`.env` 파일을 열어 다음 정보를 본인의 로컬 환경에 맞게 수정하세요:
- `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_HOST`, `DB_PORT`
- `SECRET_KEY` (보안을 위한 임의의 문자열)

### 5. 데이터베이스 설정 (MariaDB)
먼저 MariaDB에서 프로젝트용 데이터베이스를 생성합니다.
```sql
CREATE DATABASE stocklab_db;
```
그 후, 아래 명령어를 실행하여 데이터베이스 테이블을 생성합니다.
```bash
flask db upgrade
```

### 6. 애플리케이션 실행
```bash
python run.py
```
접속 주소: `http://127.0.0.1:5000`

---

## 📂 프로젝트 구조
- `app/`: Flask 애플리케이션 핵심 로직 및 블루프린트
- `migrations/`: 데이터베이스 마이그레이션 이력 관리
- `config.py`: 환경 설정 로직
- `requirements.txt`: 프로젝트 의존성 리스트
- `run.py`: 애플리케이션 진입점

## 📑 주요 라이브러리
- **Flask**: 웹 프레임워크
- **SQLAlchemy & Flask-Migrate**: ORM 및 DB 마이그레이션
- **PyMySQL**: MariaDB 연결 드라이버
- **python-dotenv**: `.env` 파일 관리

## ⚠️ 주의사항
- `.env` 파일은 보안상 절대 Git에 업로드하지 마세요. (이미 `.gitignore`에 포함되어 있습니다.)
- 새로운 라이브러리를 설치한 경우 반드시 `pip freeze > requirements.txt`를 실행하여 업데이트해 주세요.
