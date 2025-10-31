# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project is an AI agent system designed to facilitate Creative Problem Solving (CPS) and promote creative metacognition for pre-service teachers. The agent provides question-based scaffolding to help learners solve educational challenges while enhancing their metacognitive awareness.

**Target Users**: University students (pre-service teachers)
**Primary LLM**: Google Gemini API
**Core Purpose**: Promote creative metacognition through contextual scaffolding during CPS process

## Core Concepts

### Creative Problem Solving (CPS) Framework

The system guides learners through three main stages:

1. **Understanding the Challenge** (도전 이해)
   - Opportunity Construction (기회 구성): Identify beneficial goals
   - Data Exploration (자료 탐색): Investigate from multiple perspectives
   - Problem Formulation (문제 구조화): Reframe as open-ended questions

2. **Generating Ideas** (아이디어 생성)
   - Generate diverse ideas with fluency, flexibility, originality
   - Select feasible ideas

3. **Preparing for Action** (실행 준비)
   - Solution Development (해결책 고안): Refine promising ideas into actionable solutions
   - Building Acceptance (수용 구축): Plan implementation support and overcome anticipated difficulties

### Creative Metacognition Components

The agent promotes three metacognitive elements:

- **Monitoring (점검)**: Evaluate task characteristics, predict performance, assess ideas
- **Control (조절)**: Decide on task engagement, select/change strategies, choose solutions
- **Knowledge (지식)**: Activate prior experiences, update metacognitive knowledge

### Scaffolding Patterns

The agent follows specific questioning patterns for each CPS stage:

1. **Understanding Challenge**: Knowledge → Monitoring → Control (repeat)
2. **Generating Ideas**: Monitoring → Control (repeat)
3. **Preparing for Action**: Monitoring → Control (repeat) → Knowledge

## System Architecture

```
┌─────────────────┐
│  React Frontend │  ← Chat interface with real-time communication
│   (Chat UI)     │
└────────┬────────┘
         │ WebSocket
┌────────▼────────┐
│  FastAPI Server │  ← Main backend orchestrator
│  - Router       │
│  - WebSocket    │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬───────────┐
    │         │          │           │
┌───▼───┐ ┌──▼──┐ ┌─────▼─────┐ ┌──▼────┐
│Context│ │CPS  │ │Metacog.   │ │Gemini │
│Manager│ │Stage│ │Analyzer   │ │LLM    │
└───┬───┘ └──┬──┘ └─────┬─────┘ └──┬────┘
    │        │          │           │
    └────────┴──────────┴───────────┘
              │
         ┌────▼────┐
         │PostgreSQL│  ← Conversation history and session management
         └─────────┘
```

### Key Components

- **Context Manager**: Tracks conversation history and session state
- **CPS Stage Detector**: Infers current CPS stage from learner responses
- **Metacognitive Analyzer**: Identifies lacking metacognitive elements (monitoring/control/knowledge)
- **Scaffolding Generator**: Creates 1-2 sentence questions based on metacognitive needs
- **LLM Orchestrator**: Manages Gemini API calls and prompt engineering

## Design Principles

### Agent Behavior Rules

1. **Facilitate Thinking, Not Provide Answers**: The agent NEVER provides direct solutions. It only asks questions to promote learner thinking.

2. **No Forced Stage Transitions**: The agent does not push learners to next CPS stages. Transitions happen naturally when learners demonstrate sufficient depth.

3. **Context-Aware Scaffolding**: Questions are generated based on:
   - Current CPS stage
   - Lacking metacognitive elements
   - Response depth (shallow/medium/deep)
   - Conversation history

4. **Concise Questions**: All scaffolding questions must be 1-2 sentences maximum.

5. **Adaptive Questioning**: If learner provides shallow responses, continue probing with different metacognitive elements before moving forward.

### Response Depth Assessment

The system evaluates response depth using:
- Response length and specificity
- Number of ideas/causes/solutions provided
- Diversity of perspectives
- Concrete examples and details
- Connection to prior experiences

### Stage Transition Logic

Transition to next stage when:
- Minimum requirements met (e.g., ≥3 causes identified)
- Response depth consistently "deep" for 2+ exchanges
- Learner explicitly indicates readiness
- Natural conversation flow suggests completion

Prevent premature transitions by:
- Requiring minimum criteria per stage
- Limiting repeat questions (avoid infinite loops)
- Using meta-questions: "이제 다음 단계로 넘어갈 준비가 되었나요?"

## Gemini Integration

### System Prompt Structure

The Gemini API calls use a structured system prompt that includes:

1. **Role Definition**: Creative metacognition facilitator
2. **CPS Stage Descriptions**: Detailed explanation of each stage
3. **Metacognitive Elements**: Monitoring, Control, Knowledge definitions
4. **Scaffolding Examples**: Stage-specific question examples from `scaffolding.md`
5. **Behavioral Rules**: No answers, no forced transitions, assess response depth
6. **Output Format**: JSON structure with current stage, metacognitive needs, scaffolding question, transition decision

### Expected Response Format

```json
{
  "current_stage": "도전_이해_자료탐색",
  "detected_metacog_needs": ["점검", "조절"],
  "response_depth": "shallow|medium|deep",
  "scaffolding_question": "해당 문제의 난이도는 어느 정도라고 판단되나요?",
  "should_transition": false,
  "reasoning": "학습자가 문제의 원인을 1개만 제시하여 더 깊은 탐색 필요"
}
```

## Database Schema

### Sessions Table
- Stores user sessions and assignment context
- Fields: id, user_id, assignment_text, created_at, updated_at

### Conversations Table
- Stores conversation history with CPS stage and metacognitive annotations
- Fields: id, session_id, role (user/agent), message, cps_stage, metacog_elements (JSONB), created_at

### Stage Transitions Table
- Logs CPS stage transitions for analysis
- Fields: id, session_id, from_stage, to_stage, transition_reason, created_at

## Development Workflow

### Backend (FastAPI)

```bash
# Setup virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn sqlalchemy psycopg2-binary google-generativeai redis websockets

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (React + TypeScript)

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

### Database

```bash
# Start PostgreSQL (using Docker)
docker-compose up -d postgres

# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"
```

## Testing Strategy

### Unit Tests
- Test CPS stage detection logic with sample responses
- Test metacognitive element classification
- Test response depth assessment algorithms
- Test scaffolding question selection logic

### Integration Tests
- Test full conversation flow from challenge understanding to action preparation
- Test Gemini API integration with mocked responses
- Test database operations (session management, conversation logging)

### User Testing
- Conduct pilot tests with actual pre-service teachers
- Measure scaffolding question appropriateness (≥90% target)
- Measure CPS stage inference accuracy (≥85% target)
- Collect qualitative feedback on user experience

## Configuration

### Environment Variables

```bash
# Gemini API
GEMINI_API_KEY=your_gemini_api_key

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/univ_consult

# Redis (for session management)
REDIS_URL=redis://localhost:6379/0

# Application
DEBUG=true
LOG_LEVEL=info
```

### Key Configuration Files

- `.env`: Environment variables (never commit this)
- `alembic.ini`: Database migration configuration
- `docker-compose.yml`: Container orchestration for local development

## Research Considerations

This project is designed for educational research. Key considerations:

1. **Data Privacy**: Ensure all learner data is anonymized and stored securely
2. **Consent Management**: Implement proper informed consent mechanisms
3. **Experimental Design**: Support A/B testing or control group comparisons
4. **Analytics**: Track metrics for creative metacognition effectiveness
5. **Export Functionality**: Allow researchers to export conversation data for analysis

## Reference Documents

- `custom_requirement/ai_agent_design.md`: Detailed agent design specifications
- `custom_requirement/scaffolding.md`: Scaffolding question examples and metacognition framework
- `custom_requirement/question_pattern.md`: Question generation patterns per CPS stage
- `custom_requirement/create_assignmnet.md`: Sample assignment for testing

## Success Metrics

### Functional Metrics
- CPS stage inference accuracy ≥ 85%
- Appropriate scaffolding question generation rate ≥ 90%
- Average response time < 3 seconds

### User Experience Metrics
- Learner satisfaction ≥ 4.0/5.0
- Problem-solving completion rate ≥ 70%
- Average session duration: 30-60 minutes

### Research Metrics
- Demonstrated creative metacognition promotion effect
- Improved problem-solving quality vs. control group
