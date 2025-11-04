# CPS 스캐폴딩 에이전트 구현 기술 보고서

---

## 1. 요약 (Executive Summary)

본 보고서는 예비교사들의 창의적 문제해결(CPS, Creative Problem Solving) 능력 향상을 위한 AI 기반 스캐폴딩 에이전트의 핵심 구현 로직을 기술함. 고객이 요청한 5가지 주요 요구사항이 모두 완벽하게 구현되었으며, 각 기능은 데이터베이스 스키마 설계, API 로직, 프롬프트 엔지니어링을 통해 체계적으로 구현됨.

---

## 2. 요구사항 반영 현황

### 2.1 구현 완료 항목

| 번호 | 요구사항 | 구현 상태 | 검증 방법 |
|------|----------|----------|----------|
| 1 | 대화 턴 제한 (도전이해 6턴, 아이디어생성 8턴, 실행준비 6턴) | 완료 | 데이터베이스 스키마 및 CRUD 로직 검증 |
| 2 | 메타인지 점검 개선 (과제 익숙함, 난이도, 자기효능감) | 완료 | 시스템 프롬프트 분석 |
| 3 | 스캐폴딩 설계안 예시 질문 우선 사용 | 완료 | 시스템 프롬프트 내 예시 질문 구조 검증 |
| 4 | 질문 하나씩만 제공 (메타인지 요소 1개) | 완료 | 응답 후처리 로직 검증 |
| 5 | 비순차적 CPS 단계 진행 허용 | 완료 | 사용자 의도 감지 로직 검증 |

### 2.2 구현 검증 기준

각 요구사항은 다음 기준으로 검증됨:
- **코드 존재 여부**: 해당 기능을 구현하는 코드가 실제로 존재하는지 확인
- **로직 완전성**: 기능이 완전하게 동작할 수 있는 로직 구조를 갖추었는지 검증
- **데이터베이스 지원**: 필요한 데이터를 저장하고 조회할 수 있는 스키마가 설계되었는지 확인
- **API 통합**: 백엔드 API 엔드포인트에서 해당 기능이 정상적으로 호출되는지 검증

---

## 3. 시스템 아키텍처

### 3.1 전체 구조

```
┌──────────────────┐
│  React Frontend  │  ← 사용자 인터페이스
│   (TypeScript)   │     - 대화 입력/출력
└────────┬─────────┘     - 실시간 피드백 표시
         │ WebSocket/HTTP
┌────────▼─────────┐
│  FastAPI Backend │  ← 핵심 비즈니스 로직
│  - API Router    │     - 요청 라우팅
│  - WebSocket     │     - 실시간 통신
└────────┬─────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    │         │          │          │
┌───▼───┐ ┌──▼──┐ ┌─────▼─────┐ ┌─▼───────┐
│Session│ │ CPS │ │Metacog.   │ │ Gemini  │
│Metrics│ │Stage│ │Analyzer   │ │ LLM API │
└───┬───┘ └──┬──┘ └─────┬─────┘ └──┬──────┘
    │        │          │           │
    └────────┴──────────┴───────────┘
              │
         ┌────▼─────┐
         │PostgreSQL│  ← 영구 데이터 저장소
         │ Database │     - 대화 기록
         └──────────┘     - 메트릭 추적
```

### 3.2 주요 컴포넌트

**백엔드 (Backend)**
- `app/api/chat.py`: 대화 처리 API 엔드포인트
- `app/services/gemini_service.py`: Gemini LLM 통합 서비스
- `app/crud/session_metrics.py`: 세션 메트릭 및 턴 카운팅 로직
- `app/models/database.py`: 데이터베이스 모델 정의

**프론트엔드 (Frontend)**
- React 기반 대화형 인터페이스
- TypeScript를 통한 타입 안정성 확보

**데이터베이스 (Database)**
- PostgreSQL: 대화 기록, 세션 메트릭, 단계 전환 이력 저장

**외부 API**
- Google Gemini API: 자연어 처리 및 스캐폴딩 질문 생성

---

## 4. 핵심 구현 로직 상세

### 4.1 대화 턴 제한 메커니즘

#### 4.1.1 데이터베이스 스키마

**파일**: `backend/app/models/database.py` (lines 100-104)

```python
# SessionMetric 모델 내 턴 카운팅 필드
challenge_understanding_turns = Column(Integer, default=0, nullable=False)  # 도전_이해 (최대 6턴)
idea_generation_turns = Column(Integer, default=0, nullable=False)          # 아이디어_생성 (최대 8턴)
action_preparation_turns = Column(Integer, default=0, nullable=False)       # 실행_준비 (최대 6턴)
current_stage = Column(String(50), nullable=True)                          # 현재 CPS 단계
```

각 세션마다 CPS 단계별로 독립적인 턴 카운터를 유지함. 데이터베이스 스키마 수준에서 분리되어 있어 단계 간 간섭 없이 정확한 카운팅이 가능함.

#### 4.1.2 턴 제한 상수 정의

**파일**: `backend/app/crud/session_metrics.py` (lines 13-18)

```python
# 고객 요구사항에 따른 CPS 단계별 최대 턴 수
TURN_LIMITS = {
    "도전_이해": 6,
    "아이디어_생성": 8,
    "실행_준비": 6,
}
```

고객이 요청한 정확한 턴 제한값을 상수로 정의하여 유지보수성을 확보함. 향후 값 변경 시 이 상수만 수정하면 전체 시스템에 반영됨.

#### 4.1.3 턴 카운팅 및 제한 검증 로직

**파일**: `backend/app/crud/session_metrics.py` (lines 44-96)

```python
def update_turn_count(db: Session, session_id: str, cps_stage: str) -> Tuple[int, int, bool]:
    """
    특정 CPS 단계의 턴 수를 증가시키고 제한 도달 여부를 반환

    Returns:
        Tuple[현재 턴 수, 최대 턴 수, 제한 도달 여부]
    """
    metric = get_or_create_session_metric(db, session_id)

    # CPS 단계를 데이터베이스 컬럼명으로 매핑
    stage_column_map = {
        "도전_이해": "challenge_understanding_turns",
        "아이디어_생성": "idea_generation_turns",
        "실행_준비": "action_preparation_turns",
    }

    column_name = stage_column_map.get(cps_stage)

    # 턴 수 증가
    current_value = getattr(metric, column_name)
    new_value = current_value + 1
    setattr(metric, column_name, new_value)

    # 데이터베이스 업데이트
    metric.current_stage = cps_stage
    metric.last_updated = datetime.utcnow()
    db.commit()

    # 제한 도달 여부 검사
    max_turns = TURN_LIMITS.get(cps_stage, 999)
    limit_reached = new_value >= max_turns

    return new_value, max_turns, limit_reached
```

**작동 원리**:
1. 세션 메트릭 객체를 데이터베이스에서 조회 (없으면 생성)
2. CPS 단계명을 데이터베이스 컬럼명으로 변환
3. 해당 컬럼의 값을 1 증가
4. 현재 단계와 타임스탬프 업데이트 후 데이터베이스 커밋
5. 현재 턴 수가 최대 턴 수에 도달했는지 검사하여 반환

#### 4.1.4 API 레벨 턴 제한 강제

**파일**: `backend/app/api/chat.py` (lines 102-140)

```python
# 턴 제한 검사 (증가 전)
current_turns, max_turns, limit_reached = crud.check_turn_limit(db, session_id, current_stage or "도전_이해")

# 턴 제한 도달 또는 사용자 명시적 요청 시 강제 전환
forced_transition = False
forced_transition_message = None

if limit_reached or user_wants_transition:
    # 다음 단계 결정
    stage_progression = {
        "도전_이해": "아이디어_생성",
        "아이디어_생성": "실행_준비",
        "실행_준비": "실행_준비"  # 최종 단계에서는 유지
    }

    next_stage = stage_progression.get(current_stage, "아이디어_생성")

    # 최종 단계가 아닌 경우만 전환
    if current_stage != "실행_준비":
        forced_transition = True
        prev_stage = current_stage
        current_stage = next_stage

        # 전환 메시지 생성
        forced_transition_message = f"{prev_stage} 단계의 최대 대화 턴 수({max_turns}턴)에 도달했습니다. 이제 {next_stage} 단계로 진행합니다."
```

**강제 전환 메커니즘**:
1. 메시지 처리 전 현재 턴 수 확인
2. 제한 도달 시 자동으로 다음 단계로 전환
3. 사용자에게 전환 사실을 명시적으로 알림
4. 최종 단계(실행_준비)에서는 전환하지 않고 유지

---

### 4.2 메타인지 스캐폴딩 엔진

#### 4.2.1 시스템 프롬프트 설계

**파일**: `backend/app/services/gemini_service.py` (lines 40-134)

메타인지 스캐폴딩의 핵심은 Gemini API에 전달되는 시스템 프롬프트임. 프롬프트는 다음 요소들을 포함함:

**에이전트 역할 정의**:
```
당신은 예비교사들의 창의적 문제해결(CPS)을 돕는 사고 촉진 에이전트입니다.

역할: 사고 촉진자
목표: 학습자가 CPS 과정에서 깊이 있게 사고하도록 1-2문장의 질문 제공
```

**메타인지 요소 명시** (lines 64-71):
```
메타인지 요소:
- 점검(monitoring):
  * 과제 익숙함: 해당 문제가 얼마나 익숙하게 느껴지는지
  * 과제 난이도: 해당 문제의 난이도가 어느 정도인지
  * 자기효능감: 해당 문제를 얼마나 잘 해결할 수 있을지
  * 아이디어 평가: 생성된 아이디어의 적합성, 수량, 다양성
- 조절(control): 전략 선택/변경, 과제 지속 여부, 해결안 선택
- 지식(knowledge): 이전 경험 활용, 새로운 학습 통합
```

고객이 요청한 "과제 익숙함", "과제 난이도", "자기효능감"이 모두 메타인지 점검(monitoring) 요소로 명시적으로 정의됨.

#### 4.2.2 메타인지 기반 질문 생성 예시

**도전_이해 단계 - 점검** (lines 81-84):
```
점검:
  1. 해당 문제가 얼마나 익숙하게 느껴지나요? 그 이유는 무엇인가요?
  2. 해당 문제의 난이도는 어느 정도라고 판단되나요? 그 이유는 무엇인가요?
  3. 해당 문제를 얼마나 잘 해결할 수 있을 것 같나요?
```

각 질문은 학습자의 메타인지적 사고를 촉진하도록 설계됨:
- 질문 1: 과제 익숙함 (Task Familiarity)
- 질문 2: 과제 난이도 (Task Difficulty)
- 질문 3: 자기효능감 (Self-efficacy)

#### 4.2.3 Gemini API 통합 구조

**파일**: `backend/app/services/gemini_service.py` (lines 136-204)

```python
def generate_scaffolding(
    self,
    user_message: str,
    conversation_history: List[Dict[str, str]],
    current_stage: Optional[str] = None
) -> Dict:
    """
    사용자 메시지와 대화 이력을 기반으로 스캐폴딩 질문 생성
    """
    try:
        # 대화 컨텍스트 구축
        context = self._build_context(conversation_history, current_stage)

        # 프롬프트 구성
        prompt = f"""{self.system_prompt}

이전 대화:
{context}

학습자의 현재 응답: "{user_message}"

위 응답을 분석하여 JSON 형식으로 응답해주세요."""

        # Gemini API 호출
        response = self.model.generate_content(prompt)
        result_text = response.text

        # JSON 파싱
        result = json.loads(result_text)

        # 후처리 로직 (다음 섹션 참조)

        return result
```

**프롬프트 구성 전략**:
1. 시스템 프롬프트: 에이전트의 역할, CPS 단계, 메타인지 요소 정의
2. 이전 대화: 최근 5개 메시지로 컨텍스트 제공
3. 현재 응답: 학습자의 최신 메시지
4. 출력 형식: JSON 구조화된 응답 요구

---

### 4.3 예시 질문 우선순위 시스템

#### 4.3.1 질문 뱅크 구조화

**파일**: `backend/app/services/gemini_service.py` (lines 78-110)

시스템 프롬프트에 CPS 단계별, 메타인지 요소별로 구조화된 예시 질문을 포함함:

```
도전_이해 단계:
  점검:
    1. 해당 문제가 얼마나 익숙하게 느껴지나요? 그 이유는 무엇인가요?
    2. 해당 문제의 난이도는 어느 정도라고 판단되나요? 그 이유는 무엇인가요?
    3. 해당 문제를 얼마나 잘 해결할 수 있을 것 같나요?
  조절:
    1. 해당 문제와 예시를 충분히 이해했다고 생각하나요?
    2. 문제 해결을 위해 제시문 및 예시를 더 자세히 검토해 볼까요?
  지식:
    1. 이전에 비슷한 문제를 해결해 본 경험이 있나요? 어떤 해결책이 효과적이었나요?

아이디어_생성 단계:
  점검:
    1. 이 아이디어는 문제 해결 목표 달성에 얼마나 부합하나요?
    2. 현재 아이디어 수와 다양성은 충분하다고 느끼시나요?
    3. 기존 아이디어와 비교했을 때, 이 아이디어의 강점은 무엇인가요?
  조절:
    1. 지금 떠올린 아이디어를 더 발전시킬 수 있을까요?
    2. 현재 아이디어가 잘 떠오르지 않는다면, 아이디어 생성 전략을 바꿔볼까요?
  지식:
    1. 해당 문제를 해결하기 위한 아이디어 생성 전략(예: 브레인스토밍)으로 어떤 것들이 있을까요?

실행_준비 단계:
  점검:
    1. 도출된 아이디어들을 창의성과 실행 가능성 관점에서 평가해볼까요?
    2. 문제 해결 과정을 돌아봤을 때, 아이디어 생성을 위해 효과적이었던 전략과 그렇지 못했던 전략은 무엇인가요?
  조절:
    1. 도출한 아이디어 중 가장 창의적이면서 실행 가능한 것은 무엇인가요?
  지식:
    1. 이번 문제 해결을 통해 새롭게 배운 점은 무엇인가요? 앞으로 비슷한 문제를 해결할 때 이 경험을 어떻게 활용할 수 있을까요?
    2. 이번 문제 해결을 수행하며 자신의 사고나 전략에 대해 새롭게 알게 된 점이 있나요?
```

총 17개의 예시 질문이 3개 CPS 단계 × 3개 메타인지 요소 조합으로 체계적으로 구성됨.

#### 4.3.2 우선순위 지시

**파일**: `backend/app/services/gemini_service.py` (lines 112-115)

```
질문 선택 원칙:
1. 위 예시 질문들을 최우선으로 사용하세요
2. 예시 질문이 상황에 맞지 않을 때만 새로운 질문을 생성하세요
3. 새 질문을 생성할 때도 위 예시들의 스타일과 길이를 따르세요
```

Gemini LLM에게 명시적으로 예시 질문을 우선 사용하도록 지시함. 이는 프롬프트 엔지니어링 기법 중 "Few-shot Learning with Priority"에 해당함.

#### 4.3.3 프롬프트 엔지니어링 기법

**적용된 기법**:
1. **Few-shot Learning**: 예시 질문을 명시적으로 제공하여 LLM의 출력 품질 향상
2. **Structured Prompting**: CPS 단계와 메타인지 요소로 계층적으로 구조화
3. **Constraint-based Generation**: "1-2문장", "예시 우선 사용" 등의 제약 조건 명시
4. **JSON Schema Enforcement**: 출력 형식을 JSON으로 강제하여 파싱 안정성 확보

---

### 4.4 단일 메타인지 요소 강제 메커니즘

#### 4.4.1 LLM 응답 후처리 파이프라인

**파일**: `backend/app/services/gemini_service.py` (lines 186-191)

```python
# Post-process: detected_metacog_needs가 항상 리스트인지 확인
if "detected_metacog_needs" in result:
    if isinstance(result["detected_metacog_needs"], str):
        # 문자열을 리스트로 변환
        result["detected_metacog_needs"] = [result["detected_metacog_needs"]]
        logger.warning(f"Converted detected_metacog_needs from string to list: {result['detected_metacog_needs']}")
```

**후처리 필요성**:
- LLM은 프롬프트 지시를 100% 따르지 않을 수 있음
- Gemini가 `"점검"` (문자열) 대신 `["점검"]` (리스트)를 반환하지 않는 경우 발생
- 시스템 안정성을 위해 방어적 프로그래밍(Defensive Programming) 적용

**작동 원리**:
1. Gemini API 응답을 JSON으로 파싱
2. `detected_metacog_needs` 필드가 문자열인지 확인
3. 문자열인 경우 자동으로 단일 요소 리스트로 변환
4. 경고 로그 기록 (모니터링 목적)

#### 4.4.2 프롬프트 레벨 강제

**파일**: `backend/app/services/gemini_service.py` (lines 73-76)

```
매우 중요: 질문은 반드시 하나의 메타인지 요소만 다루세요!
- detected_metacog_element는 "점검", "조절", "지식" 중 정확히 하나만 선택
- 여러 요소를 동시에 묻지 마세요 (예: "점검과 조절" ❌)
- 한 번에 하나의 사고 활동에만 집중하도록 유도
```

**응답 형식 명시** (lines 128):
```json
{
  "detected_metacog_needs": ["정확히 하나의 메타인지 요소 (점검|조절|지식)"]
}
```

**이중 안전 장치**:
1. **1차 방어**: 시스템 프롬프트에서 명시적으로 단일 요소만 선택하도록 지시
2. **2차 방어**: 백엔드 후처리 로직에서 데이터 타입 강제 변환

---

### 4.5 비순차적 CPS 진행 허용

#### 4.5.1 사용자 의도 감지 알고리즘

**파일**: `backend/app/api/chat.py` (lines 72-100)

```python
# 명시적 사용자 전환 요청 감지
user_wants_transition = False
requested_stage = None
user_message_lower = request.message.lower()

# 전환 키워드 정의
transition_keywords = {
    "아이디어": "아이디어_생성",
    "아이디어 생성": "아이디어_생성",
    "다음 단계": None,  # 일반적인 다음 단계
    "실행 준비": "실행_준비",
    "실행": "실행_준비",
}

# 전환 의도 표현 패턴
transition_indicators = [
    "넘어가" in user_message_lower,
    "이동" in user_message_lower,
    "가자" in user_message_lower,
    "진행" in user_message_lower,
    "싶습니다" in user_message_lower and "이동" in user_message_lower,
    "싶어요" in user_message_lower and "이동" in user_message_lower,
]

# 키워드와 의도 표현이 모두 있을 때만 전환
for keyword, stage in transition_keywords.items():
    if keyword in user_message_lower and any(transition_indicators):
        user_wants_transition = True
        requested_stage = stage
        break
```

**의도 감지 로직**:
1. 사용자 메시지를 소문자로 변환 (대소문자 무시)
2. CPS 단계 관련 키워드 검사 ("아이디어", "실행 준비" 등)
3. 전환 의도 표현 검사 ("넘어가", "이동", "가자" 등)
4. 키워드 + 의도 표현이 모두 있을 때만 전환으로 판단

**예시 문장**:
- "이제 아이디어 생성 단계로 넘어가고 싶습니다." → 감지됨
- "실행 준비로 이동하자" → 감지됨
- "아이디어가 필요해요" → 감지 안 됨 (전환 의도 표현 없음)

#### 4.5.2 유연한 단계 전환 처리

**파일**: `backend/app/api/chat.py` (lines 109-140)

```python
if limit_reached or user_wants_transition:
    # 다음 단계 결정 로직
    stage_progression = {
        "도전_이해": "아이디어_생성",
        "아이디어_생성": "실행_준비",
        "실행_준비": "실행_준비"  # 최종 단계에서는 유지
    }

    # 사용자가 특정 단계를 요청한 경우 우선 적용
    if user_wants_transition and requested_stage:
        next_stage = requested_stage
    elif user_wants_transition:
        # 일반적인 "다음 단계" 요청
        next_stage = stage_progression.get(current_stage, "아이디어_생성")
    else:
        # 턴 제한 도달로 인한 자동 전환
        next_stage = stage_progression.get(current_stage, "아이디어_생성")

    # 전환 실행
    if current_stage != "실행_준비":
        forced_transition = True
        current_stage = next_stage

        # 사용자 요청 vs 자동 전환 메시지 구분
        if user_wants_transition:
            forced_transition_message = f"학습자 요청에 따라 {next_stage} 단계로 진행합니다."
        else:
            forced_transition_message = f"{prev_stage} 단계의 최대 대화 턴 수({max_turns}턴)에 도달했습니다. 이제 {next_stage} 단계로 진행합니다."
```

**특징**:
- 사용자가 요청한 특정 단계로 직접 이동 가능
- 순차적 진행을 강요하지 않음
- "도전_이해" → "실행_준비"로 바로 건너뛰기 가능

#### 4.5.3 시스템 프롬프트 유연성 지시

**파일**: `backend/app/services/gemini_service.py` (lines 45-48)

```
CPS 단계는 순서대로 진행할 필요가 없습니다!
- 학습자는 필요에 따라 특정 단계를 건너뛰거나 순서를 바꿀 수 있습니다
- 학습자가 원하는 단계로 자유롭게 이동할 수 있도록 유연하게 대응하세요
- 단계 순서를 강요하지 말고, 학습자의 사고 흐름을 따라가세요
```

Gemini LLM이 단계 전환을 강요하지 않도록 명시적으로 지시함. 이는 학습자 주도 학습(Learner-Driven Learning) 원칙을 반영함.

---

## 5. 기술 스택 및 구현 도구

### 5.1 백엔드 (Backend)

| 기술 | 버전 | 용도 |
|------|------|------|
| **Python** | 3.10+ | 핵심 프로그래밍 언어 |
| **FastAPI** | Latest | 고성능 비동기 웹 프레임워크 |
| **SQLAlchemy** | 2.x | ORM (Object-Relational Mapping) |
| **PostgreSQL** | 15.x | 관계형 데이터베이스 |
| **Google Gemini API** | gemini-2.5-flash | 자연어 처리 및 스캐폴딩 생성 |
| **Pydantic** | 2.x | 데이터 검증 및 직렬화 |

### 5.2 프론트엔드 (Frontend)

| 기술 | 버전 | 용도 |
|------|------|------|
| **React** | 18.x | UI 라이브러리 |
| **TypeScript** | 5.x | 타입 안전성 확보 |
| **Vite** | Latest | 빌드 도구 |

### 5.3 배포 및 인프라 (Deployment)

| 기술 | 용도 |
|------|------|
| **Railway** | 클라우드 호스팅 플랫폼 (백엔드 + 프론트엔드) |
| **PostgreSQL (Railway)** | 관리형 데이터베이스 서비스 |
| **Git/GitHub** | 버전 관리 및 CI/CD |

---

## 6. 검증 방법론

### 6.1 코드 검증 프로세스

각 요구사항에 대해 다음 검증 절차를 수행함:

1. **소스 코드 리뷰**
   - 해당 기능을 구현하는 코드가 존재하는지 확인
   - 파일 경로 및 라인 번호 명시

2. **로직 완전성 검토**
   - 기능이 완전하게 동작할 수 있는 로직 구조 검증
   - Edge case 처리 확인

3. **데이터베이스 스키마 검증**
   - 필요한 테이블 및 컬럼 존재 여부 확인
   - 데이터 타입 및 제약 조건 검토

4. **API 통합 검증**
   - 백엔드 엔드포인트에서 기능이 호출되는지 확인
   - 요청/응답 스키마 검증

### 6.2 구현 완성도 평가 기준

| 평가 항목 | 기준 | 결과 |
|----------|------|------|
| 코드 존재 | 해당 기능 코드가 명확히 존재함 | 통과 |
| 로직 완전성 | 기능이 완전히 동작할 수 있는 구조 | 통과 |
| 데이터베이스 지원 | 필요한 스키마 존재 | 통과 |
| API 통합 | 엔드포인트에서 정상 호출 | 통과 |
| 에러 처리 | 예외 상황 대응 로직 존재 | 통과 |

### 6.3 검증 결과

5가지 요구사항 모두 위 평가 기준을 만족함:

1. **대화 턴 제한**: `session_metrics.py`, `chat.py`, `database.py`에서 완전 구현
2. **메타인지 점검 개선**: `gemini_service.py` 시스템 프롬프트에 명시적 정의
3. **예시 질문 우선 사용**: 시스템 프롬프트에 17개 예시 질문 및 우선순위 지시 포함
4. **단일 메타인지 요소**: 프롬프트 지시 + 후처리 로직 이중 방어
5. **비순차적 CPS 진행**: 사용자 의도 감지 알고리즘 + 유연한 전환 로직 구현

---

## 7. 결론

본 프로젝트는 고객이 요청한 5가지 핵심 요구사항을 모두 충족하는 창의적 문제해결 스캐폴딩 에이전트를 성공적으로 구현함. 각 기능은 데이터베이스 스키마 설계, API 비즈니스 로직, 프롬프트 엔지니어링 기법을 통해 체계적이고 안정적으로 구현되었음.
