# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

意图解析 (Intent Parsing) is a Chinese WebUI for intelligent computing business workflows. It uses a Vue 3 frontend with a Python FastAPI backend to handle intent parsing for video AI inference and model training business types.

## Development Commands

### Frontend (thchat-ui/)
```bash
cd thchat-ui
npm install
npm run serve      # Dev server at http://localhost:8080
npm run build      # Production build
```

### Backend (server/)
```bash
cd server
# Run the FastAPI server at http://0.0.0.0:6000
python idn_agent.py
```

## Architecture

### Frontend (`thchat-ui/`)
- Vue 3 + Element Plus + Vuex + Vue Router
- Uses IndexedDB for local data persistence (no backend database needed for frontend)
- Supports multiple LLM platform integrations

### Backend (`server/`)

**Core Entry Point:** `server/idn_agent.py`
- FastAPI app exposing `/chat/stream` and `/chat/slot_extract` endpoints
- Uses `ChatTongyi` (LangChain) as the LLM

**Parser Layer (`server/parser/`)**
- `state.py`: Pydantic `State` model tracking workflow state
- `state_parser.py`: Parses LLM text output into structured `State` - extracts JSON, validates parameters, populates DAG templates
- `dag_template.py`: Contains `VIDEO_DAG_TEMPLATE` and `TRAIN_DAG_TEMPLATE`

**Prompt Layer (`server/prompt/`)**
- `workflow_parse_intent.py`: Two-stage parsing prompts - `get_slot_parse_prompt()` for initial extraction, `get_followup_parse_prompt()` for completion/follow-up
- `workflow_dag.py`: DAG execution prompts

**API Layer (`server/api/`)**
- `db_api.py`: FastAPI router for chat session CRUD at `/session/`

**Database Layer (`server/model/`, `server/crud/`, `server/util/`)**
- SQLAlchemy ORM models and CRUD operations
- Session storage via SQLite

## State Model

```python
class State(BaseModel):
    session_id: str
    workflow: str          # "intent_parsing" or "dag"
    stage: str             # "intent_parsing", "ask_missing", "complete"
    parse_success: bool
    missing_params: list   # Required but not provided
    reason_params: list    # Provided but invalid
    intent_result: dict   # Raw LLM JSON output
    dag: dict             # Populated from template when parse_success
    code: int
    msg: str
```

## Intent Parsing Workflow

1. **Slot Extraction**: User input → LLM → extract business type + parameters
2. **Validation**: Check required params against business type templates
3. **Follow-up/Completion**: If params missing/invalid, prompt user to fill them
4. **DAG Population**: When all params valid, fill `VIDEO_DAG_TEMPLATE` or `TRAIN_DAG_TEMPLATE`

## Business Types & Parameters

| Business Type | Required Params |
|--------------|-----------------|
| 视频AI推理 (Video AI Inference) | 模型名称, 延迟, 视频帧率, 分辨率, 模态, 开始时间, 期望运行时间 |
| AI模型训练 (AI Model Training) | 模型名称, 数据集, 训练轮次, 模态, 开始时间, 期望运行时间 |

## Key Files

- `server/idn_agent.py:147` - `/chat/stream` endpoint entry point
- `server/parser/state_parser.py:46` - `parse_intent_output()` - main parsing logic
- `server/prompt/workflow_parse_intent.py` - Prompt templates
- `server/parser/dag_template.py` - DAG structure templates
