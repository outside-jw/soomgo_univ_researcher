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

- **Context Manager**: Tracks conversation history and session state (implemented in CRUD operations)
- **CPS Stage Detector**: Infers current CPS stage from learner responses (Gemini-based)
- **Metacognitive Analyzer**: Identifies lacking metacognitive elements (Gemini-based)
- **Scaffolding Generator**: Creates 1-2 sentence questions based on metacognitive needs (Gemini-based)
- **LLM Orchestrator**: `GeminiService` class manages API calls and prompt engineering

### Implementation Architecture

**Backend Structure** (`backend/app/`):
```
app/
├── main.py                    # FastAPI app, CORS, SPA serving, lifespan events
├── api/
│   ├── chat.py               # Chat endpoints (session, message)
│   └── research.py           # Research data export (sessions, CSV)
├── services/
│   └── gemini_service.py     # GeminiService class (singleton)
├── crud/
│   ├── sessions.py           # Session CRUD operations
│   ├── conversations.py      # Conversation CRUD operations
│   ├── stage_transitions.py # Stage transition logging
│   └── session_metrics.py   # Session metrics calculation
├── models/
│   ├── database.py           # SQLAlchemy models (Session, Conversation, etc.)
│   └── schemas.py            # Pydantic schemas for API
├── db/
│   ├── session.py            # Database session management
│   └── migrations.py         # Custom migration scripts
├── core/
│   └── config.py             # Configuration and settings
└── resources/
    └── question_bank.py      # Fallback questions if Gemini fails
```

**Frontend Structure** (`frontend/src/`):
```
src/
├── App.tsx                   # Main app with routing
├── components/
│   ├── ChatInterface.tsx     # Main chat UI
│   ├── AssignmentCard.tsx    # Assignment display
│   ├── CPSProgressStepper.tsx      # Visual CPS stage indicator
│   ├── EnhancedMessageCard.tsx     # Message bubbles with metadata
│   ├── MetacognitionSidebar.tsx    # Metacognition element display
│   ├── StageTransitionNotification.tsx  # Stage change alerts
│   ├── AdminLogin.tsx        # Admin authentication
│   ├── AdminSessionList.tsx  # Session list for admin
│   └── AdminConversationView.tsx   # Detailed conversation view
├── services/
│   └── api.ts                # API client (Axios)
├── types/
│   └── index.ts              # TypeScript type definitions
└── constants/
    └── scaffolding.ts        # CPS stage and metacog definitions
```

**Key Implementation Details**:

1. **GeminiService (`backend/app/services/gemini_service.py:18`)**:
   - Singleton pattern with `gemini_service` module-level instance
   - `__init__` method builds comprehensive system prompt from question bank
   - `generate_scaffolding()` sends user message + context → receives JSON response
   - `_build_context()` limits conversation history to last 6 messages (MAX_CONTEXT_MESSAGES)
   - `_create_fallback_response()` provides default questions if Gemini fails

2. **Chat API (`backend/app/api/chat.py`)**:
   - Session-based conversation tracking (session must exist before sending messages)
   - Stores user messages and agent responses in database
   - Logs stage transitions when detected
   - Returns scaffolding data alongside agent message

3. **Database Models (`backend/app/models/database.py`)**:
   - `Session`: User sessions with assignment context
   - `Conversation`: Individual messages with CPS stage and metacog annotations
   - `StageTransition`: Logs of stage changes for analysis
   - `SessionMetric`: Aggregated metrics per session

4. **Frontend State Management**:
   - Uses Zustand for global state (admin auth)
   - Component-local state for chat interface
   - React Router for admin/user route separation

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

### Backend Setup and Development

```bash
# Navigate to backend directory
cd backend

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Run development server (uses in-memory SQLite by default)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**API Documentation**: Available at http://localhost:8000/docs (FastAPI Swagger UI)

### Frontend Setup and Development

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

**Default Port**: http://localhost:5173 (Vite default)

### Testing

```bash
# Backend tests (from backend/ directory)
pytest                          # Run all tests
pytest tests/test_api.py        # Run specific test file
pytest -v                       # Verbose output
pytest -k "test_name"           # Run specific test by name

# Frontend linting
cd frontend
npm run lint
```

### Production Build

```bash
# Build frontend
cd frontend
npm run build

# Copy built files to backend static directory
cp -r dist ../backend/static

# The backend serves the frontend from /backend/static/
# Access at http://localhost:8000/ when backend is running
```

### Database Migrations

This project uses **custom migration scripts** (not Alembic):

```bash
# Migrations run automatically on server startup via start.sh
# To run manually:
python -c "from app.db.migrations import migrate_add_turn_tracking_columns; migrate_add_turn_tracking_columns()"

# Database tables are created automatically if they don't exist
# See backend/app/models/database.py for schema definitions
```

**Note**: The system uses SQLite in-memory for development/testing and PostgreSQL for production (Railway).

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

**Backend (.env)**:
```bash
# Required
GEMINI_API_KEY=your_gemini_api_key

# Optional (with defaults)
DATABASE_URL=postgresql://user:password@localhost:5432/univ_consult  # Auto-configured on Railway
GEMINI_MODEL=gemini-2.0-flash-exp
DEBUG=true
LOG_LEVEL=info
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

**Frontend (.env)**:
```bash
# Required for production
VITE_API_URL=https://your-backend.railway.app

# Required for admin access
VITE_ADMIN_PASSWORD=your_secure_password
```

### Key Configuration Files

- `backend/.env`: Backend environment variables (never commit this)
- `frontend/.env`: Frontend environment variables (never commit this)
- `backend/.env.example`: Template for backend environment variables
- `railway.toml`: Railway deployment configuration (root level)
- `backend/railway.json`: Backend service configuration
- `frontend/railway.json`: Frontend service configuration
- `backend/start.sh`: Startup script with migrations

## Admin Interface

The system includes an admin interface for researchers to view and export conversation data:

**Access**: Navigate to `/admin` in the deployed frontend

**Authentication**: Requires password set in `VITE_ADMIN_PASSWORD` environment variable

**Features**:
- View all conversation sessions
- Filter by user ID
- View detailed conversation history with CPS stage annotations
- Export session data to CSV for analysis
- View session metrics (turn counts, stage transitions, response depth)

**Admin Routes** (React Router):
- `/admin` - Login page
- `/admin/sessions` - Session list
- `/admin/session/:id` - Detailed conversation view

## Railway Deployment

### Deployment Architecture

The project is deployed as a **monolithic service** on Railway:
- **Single service** serves both backend API and frontend static files
- **PostgreSQL database** auto-provisioned by Railway
- **Environment variables** managed through Railway dashboard

### Deployment Configuration

**Root-level `railway.toml`**:
- Defines build and start commands
- Runs database migrations on startup
- Health check on `/health` endpoint
- Auto-restart on failure

**Startup Sequence**:
1. Install Python dependencies (`pip install -r requirements.txt`)
2. Run database migrations (`app.db.migrations.migrate_add_turn_tracking_columns()`)
3. Start uvicorn server with 2 workers
4. Serve React frontend from `/backend/static/`

### Triggering Deployments

Railway auto-deploys on git push to connected branch. To manually trigger:
```bash
# Touch deploy trigger file
touch backend/DEPLOY_TRIGGER.txt
git add backend/DEPLOY_TRIGGER.txt
git commit -m "trigger: Railway redeploy"
git push
```

### Environment Variables on Railway

**Required**:
- `GEMINI_API_KEY` - Google Gemini API key
- `VITE_ADMIN_PASSWORD` - Admin interface password (frontend)

**Auto-configured**:
- `DATABASE_URL` - PostgreSQL connection (provided by Railway)
- `PORT` - Server port (provided by Railway)

**Optional**:
- `ALLOWED_ORIGINS` - CORS origins (defaults to Railway domain)
- `GEMINI_MODEL` - Model version (defaults to gemini-2.0-flash-exp)
- `ENVIRONMENT` - Environment name (production/staging)

### Pre-Deployment Checklist

1. **Build frontend and copy to backend**:
   ```bash
   cd frontend
   npm run build
   cp -r dist ../backend/static
   git add ../backend/static
   git commit -m "build: Update frontend static files"
   ```

2. **Verify environment variables** in Railway dashboard

3. **Test health endpoint** after deployment: `https://your-app.railway.app/health`

4. **Verify admin password** is set for admin interface access

## Research Considerations

This project is designed for educational research. Key considerations:

1. **Data Privacy**: Ensure all learner data is anonymized and stored securely
2. **Consent Management**: Implement proper informed consent mechanisms
3. **Experimental Design**: Support A/B testing or control group comparisons
4. **Analytics**: Track metrics for creative metacognition effectiveness
5. **Export Functionality**: Allow researchers to export conversation data for analysis

## Important Development Patterns

### Adding New Scaffolding Questions

Edit `backend/app/resources/question_bank.py` to modify the system prompt and question examples:
- Add stage-specific questions to respective sections
- Include metacognition element annotations (지식/점검/조절)
- Update behavioral rules if changing agent logic

### Modifying CPS Stages

1. Update stage definitions in `backend/app/resources/question_bank.py`
2. Update frontend constants in `frontend/src/constants/scaffolding.ts`
3. Update stage transition logic in Gemini prompt (if needed)
4. Test stage inference with sample conversations

### Database Schema Changes

Since this project uses **custom migrations** (not Alembic):
1. Modify models in `backend/app/models/database.py`
2. Create migration function in `backend/app/db/migrations.py`
3. Add migration call to `backend/start.sh`
4. Test locally with SQLite before deploying
5. Migration runs automatically on Railway deployment

### Adding New API Endpoints

1. Define Pydantic schemas in `backend/app/models/schemas.py`
2. Add endpoint to appropriate router (`api/chat.py` or `api/research.py`)
3. Add CRUD operations to `backend/app/crud/` if database access needed
4. Update frontend API client in `frontend/src/services/api.ts`
5. Document in API docs (FastAPI auto-generates from docstrings)

### Frontend Component Development

- **Styling**: Uses CSS modules (`.css` files alongside `.tsx`)
- **Design tokens**: Global styles in `frontend/src/styles/design-tokens.css`
- **Type safety**: Define types in `frontend/src/types/index.ts`
- **API calls**: Use functions from `api.ts`, not direct Axios calls
- **Routing**: Protected admin routes use `ProtectedRoute` component

## Reference Documents

- `custom_requirement/ai_agent_design.md`: Detailed agent design specifications
- `custom_requirement/scaffolding.md`: Scaffolding question examples and metacognition framework
- `custom_requirement/question_pattern.md`: Question generation patterns per CPS stage
- `custom_requirement/create_assignmnet.md`: Sample assignment for testing
- `RAILWAY_DEPLOYMENT.md`: Detailed Railway deployment guide (Korean)
- `backend/IMPLEMENTATION_REPORT.md`: Backend implementation details
- `backend/TEST_REPORT.md`: Test coverage and results
- `GUI_TEST_REPORT.md`: Frontend testing results

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
