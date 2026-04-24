# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

意图解析 (Intent Parsing) is a Chinese WebUI for intelligent computing business workflows. It uses a Vue 3 frontend with a Python FastAPI backend to handle intent parsing for video AI inference and model training business types.

## Project Context

- **Primary languages**: Python (backend), JavaScript (Vue frontend)
- **Domain**: Distributed training system with GPU nodes, MinIO storage, and REST API
- **Common workflows**: Intent parsing, training orchestration, Docker deployment to private registry

## Before Implementing

- For **deployment/infrastructure tasks**: confirm the target OS/environment first
- For **multi-step workflows**: show the proposed approach and wait for confirmation before executing
- If unsure about best approach, ask rather than picking one that may be wrong

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

## Docker/Deployment Conventions

- **Always specify OS/distribution** when using Docker networking — `host.docker.internal` is Linux-incompatible; use `network: host` or explicit IP instead
- Always verify deploy.sh script works from the actual deployment location, not relative to project root
- Include `.dockerignore` in every project before first build to avoid node_modules bloat
- For Vue/Node apps: **proxy only works in dev mode**; production needs nginx config

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
    reason_params: list   # Provided but invalid
    intent_result: dict   # Raw LLM JSON output
    dag: dict             # Populated from template when parse_success
    code: int
    msg: str
    original_input: str    # Preserved user input for strategy detection
```

## Routing Strategies

Four routing strategies supported via `policy_type` in DAG:

| Strategy | Keywords | Description |
|----------|----------|-------------|
| RESOURCE_GUARANTEE | (default) | Resource-first routing |
| TIME_CONSTRAINED | 更快, 最快, 尽快, 高速, 实时... | Time-sensitive tasks |
| COST_CONSTRAINED | 成本更低, 便宜, 省钱... | Cost-optimized routing |
| LOAD_BALANCE | 负载均衡, 不排队, 高并发... | Load distribution |

## Intent Parsing Workflow

1. **Slot Extraction**: User input → LLM → extract business type + parameters
2. **Validation**: Check required params against business type templates
3. **Follow-up/Completion**: If params missing/invalid, prompt user to fill them
4. **Strategy Detection**: Detect routing strategy from user input keywords
5. **DAG Population**: When all params valid, fill DAG template with policy_type and modal

## Business Types & Parameters

| Business Type | Required Params |
|--------------|-----------------|
| 视频AI推理 (Video AI Inference) | 模型名称, 延迟, 视频帧率, 分辨率, 模态, 开始时间, 期望运行时间, 源终端, 目的终端 |
| 模型训练 (Model Training) | 模型名称, 数据集, 训练轮次, 模态, 开始时间, 期望运行时间, 训练完成时间, 源终端, 目的终端 |

### Parameter Normalization
- "训练轮数" / "轮数" / "n轮" → "训练轮次"
- "完成时间要求" / "完成时间" → "训练完成时间"
- Resolution aliases: "4k"→"3840x2160", "1080p"→"1920x1080", "720p"→"1280x720"

## Key Files

- `server/idn_agent.py:147` - `/chat/stream` endpoint entry point
- `server/parser/state_parser.py:114` - `parse_intent_output()` - main parsing logic
- `server/parser/state_parser.py:43` - `detect_routing_strategy()` - strategy detection
- `server/prompt/workflow_parse_intent.py` - Prompt templates
- `server/parser/dag_template.py` - DAG structure templates
- `server/config/business_config.py` - Centralized business configuration and validation
