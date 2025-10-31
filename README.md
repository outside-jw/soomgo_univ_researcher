# CPS 스캐폴딩 에이전트 (Creative Problem Solving Scaffolding Agent)

예비교사들의 창의적 문제해결(CPS)을 돕는 AI 에이전트 시스템

## 프로젝트 개요

이 프로젝트는 예비교사들이 학교 현장의 문제를 창의적으로 해결할 수 있도록 메타인지를 촉진하는 AI 에이전트입니다. 질문 기반 스캐폴딩을 제공하여 학습자가 문제를 더 깊이 사고하고 실행 가능한 해결책을 도출하도록 돕습니다.

## 주요 기능

- 🤖 **지능형 스캐폴딩**: 학습자 응답을 분석하여 적절한 질문 생성
- 🎯 **CPS 단계 추론**: 현재 문제해결 단계 자동 판단
- 🧠 **메타인지 촉진**: 점검, 조절, 지식 요소를 균형있게 촉진
- 💬 **자연스러운 대화**: 1-2문장의 간결한 질문으로 사고 유도
- 📊 **실시간 피드백**: 단계별 진행 상황 및 메타인지 요소 표시

## 기술 스택

### Backend
- **FastAPI**: Python 웹 프레임워크
- **Google Gemini**: LLM 기반 스캐폴딩 생성
- **SQLAlchemy**: 데이터베이스 ORM
- **PostgreSQL**: 대화 이력 저장

### Frontend
- **React + TypeScript**: UI 프레임워크
- **Vite**: 빌드 도구
- **Axios**: API 통신

### 배포
- **Railway**: 클라우드 플랫폼
- **Docker**: 컨테이너화

## 로컬 개발 환경 설정

### 1. Backend 설정

```bash
# 백엔드 디렉터리로 이동
cd backend

# Python 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일을 열어 GEMINI_API_KEY 설정

# 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

서버가 실행되면 http://localhost:8000 에서 접속 가능합니다.
- API 문서: http://localhost:8000/docs

### 2. Frontend 설정

```bash
# 프론트엔드 디렉터리로 이동
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

프론트엔드가 실행되면 http://localhost:3000 에서 접속 가능합니다.

## Railway 배포

### Backend 배포

1. Railway 프로젝트 생성
2. GitHub 저장소 연결
3. `backend` 디렉터리를 Root Directory로 설정
4. 환경변수 설정:
   - `GEMINI_API_KEY`: Google Gemini API 키
   - `DATABASE_URL`: PostgreSQL URL (Railway가 자동 제공)
   - `ALLOWED_ORIGINS`: 프론트엔드 URL

### Frontend 배포

1. 새로운 Railway 서비스 생성
2. `frontend` 디렉터리를 Root Directory로 설정
3. 환경변수 설정:
   - `VITE_API_URL`: 백엔드 API URL

## API 엔드포인트

### POST `/api/chat/message`
학습자 메시지를 받아 스캐폴딩 질문 생성

**Request:**
```json
{
  "session_id": "optional-uuid",
  "message": "학생들이 수업에 집중하지 않아요",
  "conversation_history": [],
  "current_stage": "optional-stage"
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "agent_message": "그 상황에서 학생들이 보인 구체적인 행동은 무엇이었나요?",
  "scaffolding_data": {
    "current_stage": "도전_이해_자료탐색",
    "detected_metacog_needs": ["점검"],
    "response_depth": "shallow",
    "scaffolding_question": "그 상황에서 학생들이 보인 구체적인 행동은 무엇이었나요?",
    "should_transition": false,
    "reasoning": "문제의 구체적 상황 파악 필요"
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

### POST `/api/chat/session`
새로운 대화 세션 생성

### GET `/api/chat/health`
서버 상태 확인

## CPS 단계

1. **도전 이해** (Understanding the Challenge)
   - 기회 구성: 문제 해결의 건설적 목표 식별
   - 자료 탐색: 다양한 관점에서 핵심 요소 파악
   - 문제 구조화: 개방형 질문 형태로 재구성

2. **아이디어 생성** (Generating Ideas)
   - 유창성, 유연성, 독창성 기반 아이디어 생성
   - 실행 가능성 높은 아이디어 선별

3. **실행 준비** (Preparing for Action)
   - 해결책 고안: 실행 가능한 해결책으로 구체화
   - 수용 구축: 실행 계획 및 어려움 극복 방법 고민

## 메타인지 요소

- **점검 (Monitoring)**: 과제 특성 평가, 수행 예측, 아이디어 평가
- **조절 (Control)**: 전략 선택/변경, 과제 지속 여부, 해결안 선택
- **지식 (Knowledge)**: 이전 경험 활용, 새로운 학습 통합

## 프로젝트 구조

```
univ_consult/
├── backend/
│   ├── app/
│   │   ├── api/          # API 엔드포인트
│   │   ├── core/         # 설정 및 공통 모듈
│   │   ├── models/       # 데이터 모델
│   │   └── services/     # 비즈니스 로직 (Gemini 통합)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/   # React 컴포넌트
│   │   ├── services/     # API 통신
│   │   └── types/        # TypeScript 타입
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf
├── custom_requirement/   # 프로젝트 설계 문서
└── CLAUDE.md            # 개발 가이드
```

## 라이센스

이 프로젝트는 교육 연구 목적으로 개발되었습니다.

## 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 등록해주세요.
