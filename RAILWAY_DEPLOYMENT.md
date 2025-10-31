# Railway 배포 가이드

## 배포 전 체크리스트

### 1. 환경 설정 확인
- [ ] Gemini API 키 확보 (https://makersuite.google.com/app/apikey)
- [ ] Railway 계정 생성 (https://railway.app)
- [ ] Railway CLI 설치 (선택사항)
  ```bash
  npm i -g @railway/cli
  ```

### 2. 프론트엔드 빌드
```bash
cd frontend
npm install
npm run build

# 빌드된 파일을 backend/static으로 복사
cp -r dist ../backend/static
```

### 3. Backend 의존성 확인
```bash
cd backend
pip install -r requirements.txt
```

### 4. 로컬 테스트
```bash
# Backend 서버 실행
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Health check 확인
curl http://localhost:8000/health
# 응답: {"status":"healthy","version":"1.0.0","environment":"production"}

# API 테스트
curl http://localhost:8000/
```

## Railway 배포 단계

### Step 1: Railway 프로젝트 생성

1. Railway 대시보드 접속: https://railway.app/new
2. "Deploy from GitHub repo" 선택
3. GitHub 저장소 연결 및 선택

또는 CLI 사용:
```bash
railway login
railway init
```

### Step 2: PostgreSQL 데이터베이스 추가

1. Railway 프로젝트에서 "New" → "Database" → "PostgreSQL" 선택
2. 데이터베이스가 자동으로 생성됨
3. `DATABASE_URL` 환경변수가 자동으로 주입됨

### Step 3: 환경변수 설정

Railway Dashboard → 프로젝트 → Variables 에서 다음 환경변수 추가:

```bash
# 필수 환경변수
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=${{Postgres.DATABASE_URL}}  # Railway가 자동 주입
ALLOWED_ORIGINS=https://your-app.railway.app

# 선택 환경변수
DEBUG=false
LOG_LEVEL=info
ENVIRONMENT=production
GEMINI_MODEL=gemini-2.0-flash-exp
PORT=8000
HOST=0.0.0.0
```

**중요**: `GEMINI_API_KEY`는 반드시 설정해야 합니다!

### Step 4: 배포 설정 확인

`backend/railway.json` 파일이 다음과 같이 설정되어 있는지 확인:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

### Step 5: 배포 실행

#### GitHub 자동 배포 (권장)
1. 코드를 GitHub에 push
2. Railway가 자동으로 감지하고 배포 시작
3. 배포 로그 확인

#### CLI 수동 배포
```bash
cd backend
railway up
```

### Step 6: 배포 확인

1. Railway Dashboard에서 배포 로그 확인
2. "Deployments" 탭에서 상태 확인
3. 생성된 도메인 접속: `https://your-app.railway.app`
4. Health check 확인:
   ```bash
   curl https://your-app.railway.app/health
   ```

### Step 7: 도메인 설정 (선택사항)

Custom domain 사용 시:
1. Railway Dashboard → Settings → Domains
2. "Custom Domain" 클릭
3. 도메인 입력 및 DNS 레코드 추가
4. `.env`의 `ALLOWED_ORIGINS`에 도메인 추가

## 배포 후 확인사항

### 1. Health Check 확인
```bash
curl https://your-app.railway.app/health
```
예상 응답:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production"
}
```

### 2. Database 연결 확인
Railway Dashboard → PostgreSQL → Metrics에서 연결 상태 확인

### 3. 로그 모니터링
```bash
# CLI로 로그 확인
railway logs

# 또는 Dashboard에서 실시간 로그 확인
```

### 4. 성능 모니터링
Railway Dashboard → Metrics:
- CPU 사용률 (목표: <50%)
- Memory 사용률 (목표: <60%)
- Request Rate
- Response Time (목표: <3초)

## 실험 당일 체크리스트

### 사전 준비 (실험 1시간 전)
- [ ] Railway 서비스 상태 확인 (https://status.railway.app)
- [ ] Health check 정상 응답 확인
- [ ] Database 연결 상태 확인
- [ ] Gemini API quota 여유 확인 (60 RPM)
- [ ] 백업 연락 방법 준비 (참여자용)

### 실험 중 모니터링
- [ ] Railway Dashboard에서 실시간 로그 모니터링
- [ ] CPU/Memory 사용률 확인
- [ ] Error rate 확인
- [ ] Response time 확인

### 실험 후
- [ ] 모든 세션 데이터 백업
  ```bash
  railway run pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
  ```
- [ ] 로그 다운로드 및 보관
- [ ] 참여자 피드백 수집

## 트러블슈팅

### 배포 실패 시

**문제**: Build 실패
```
해결방법:
1. requirements.txt 확인
2. Python 버전 확인 (runtime.txt)
3. Railway 로그에서 에러 메시지 확인
```

**문제**: Health check 실패
```
해결방법:
1. /health 엔드포인트 정상 동작 확인
2. 환경변수 설정 확인
3. Database 연결 상태 확인
```

**문제**: Database 연결 실패
```
해결방법:
1. DATABASE_URL 환경변수 확인
2. PostgreSQL 서비스 상태 확인
3. Connection pooling 설정 확인
```

### 성능 문제

**문제**: Response 시간 느림
```
해결방법:
1. Worker 수 증가 (railway.json에서 --workers 2 → 4)
2. Database 쿼리 최적화
3. Gemini API 응답 시간 확인
```

**문제**: Memory 부족
```
해결방법:
1. Railway Plan 업그레이드
2. Connection pool 크기 조정 (pool_size=5 → 3)
3. Worker 수 감소
```

**문제**: Gemini API Rate Limit
```
해결방법:
1. API quota 확인 (60 RPM)
2. Rate limiting 구현 확인
3. 필요 시 Pay-as-you-go 전환
```

## 비용 관리

### 예상 월 비용 (30명 규모)
```
Railway Developer Plan:        $20
PostgreSQL (2GB storage):       $5
추가 실행 시간:                  $5
──────────────────────────────
총 예상 비용:                    $30/월
```

### Gemini API 비용
```
Free tier: 60 RPM (분당 요청)
예상 사용량: ~4,500 메시지/월
→ 무료 할당량으로 충분

초과 시: $0.00025/요청 → ~$5/월
```

### 비용 최적화 팁
1. 사용하지 않을 때 서비스 일시 중지
2. Development Plan으로 충분 (Enterprise 불필요)
3. Database 크기 모니터링 (2GB 이내 유지)
4. 로그 보관 기간 설정

## 데이터 백업

### 자동 백업 설정
Railway Dashboard → PostgreSQL → Backups
- Enable automatic daily backups

### 수동 백업
```bash
# 로컬로 백업
railway run pg_dump $DATABASE_URL > backup.sql

# 백업 복원
railway run psql $DATABASE_URL < backup.sql
```

## 보안 체크리스트

- [ ] 환경변수에 민감 정보 저장 (코드에 하드코딩 금지)
- [ ] CORS 올바른 origin만 허용
- [ ] HTTPS 강제 (Railway 자동 제공)
- [ ] API rate limiting 구현 (Gemini API)
- [ ] 개인정보 익명화 처리
- [ ] 데이터베이스 접근 제한 (Railway 자동)

## 참고 링크

- Railway 공식 문서: https://docs.railway.app
- Gemini API 문서: https://ai.google.dev/docs
- FastAPI 배포 가이드: https://fastapi.tiangolo.com/deployment/
- PostgreSQL 모범 사례: https://wiki.postgresql.org/wiki/Performance_Optimization

## 지원 및 문의

Railway 문제:
- Railway Discord: https://discord.gg/railway
- Status 페이지: https://status.railway.app

Gemini API 문제:
- Google AI Forum: https://discuss.ai.google.dev/

프로젝트 관련:
- GitHub Issues: [저장소 주소]
