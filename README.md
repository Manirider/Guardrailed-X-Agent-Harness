# Guardrailed X Agent Harness

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?logo=pydantic&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-Browser%20Automation-2EAD33?logo=playwright&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

> A production-grade, deterministic agent harness for scheduled social media posting, engineered with Playwright browser automation, strict Pydantic v2 validation, and multi-stage deterministic safety guardrails.

## Executive Summary

Traditional "god-prompt" agent architectures grant large language models autonomous control over scheduling decisions, browser operations, and safety policies. In production systems, this unconstrained autonomy results in hallucinated URLs, unauthorized account mentions, silent run failures, and ungrounded social media output.

**Guardrailed X Agent Harness** enforces a strict architectural boundary: **deterministic Python controls the system, while the LLM acts solely as a constrained text transformer**. Scheduling, state persistence, browser execution, and safety enforcement are completely decoupled from the model, ensuring zero ungrounded actions and dependable reproducibility.

## Core Design Principles

- **Deterministic Control Flow**: Python coordinates every lifecycle phase. The LLM never initiates actions or decides execution branches.
- **Defense-in-Depth Validation**: Model outputs must pass strict Pydantic v2 schemas and a sequential chain of deterministic safety checks before browser dispatch.
- **Fail-Closed Fallback Architecture**: If an LLM response violates safety policies or produces schema anomalies, the system automatically reverts to validated raw source content.
- **Full Execution Observability**: Every execution run emits structured JSONL telemetry containing entity diffs, timing benchmarks, guardrail trigger classifications, and browser outcomes.

## System Architecture

The harness is structured as a unidirectional pipeline with strict boundary separation:

```
[ CSV Input Schedule ]
          │
          ▼
[ Scheduler Engine ] ──► Queries due row for UTC date (filters duplicates)
          │
          ▼
[ State Manager ] ────► Verifies execution status against posted history
          │
          ▼
[ LLM Formatter ] ────► Constrained model transforms raw text to tweet format
          │
          ▼
[ Pydantic Validator ] ─► Schema validation (extra fields forbidden)
          │
          ▼
[ Guardrail Chain ] ──► Length check + Banned terms + Groundedness verification
          │
          ├── (Pass) ───► Candidate LLM text approved
          └── (Fail) ───► Graceful fallback to verified raw text
          │
          ▼
[ HITL Gate ] ────────► Optional human-in-the-loop review (when configured)
          │
          ▼
[ Playwright Actor ] ─► Authenticated session post to mock social platform
          │
          ▼
[ Observability ] ────► Emits end-to-end trace log (traces.jsonl)
```

## Repository Structure

```
guardrailed-x-agent-harness/
├── src/harness/
│   ├── __init__.py
│   ├── agent.py               # Main orchestration harness engine
│   ├── browser_actor.py       # Playwright browser automation with session caching
│   ├── cli.py                 # Command line interface entrypoint
│   ├── config.py              # Centralized environment configuration
│   ├── guardrails.py          # Deterministic safety rule chain
│   ├── llm_formatter.py       # Structured LLM invocation client
│   ├── models.py              # Pydantic v2 data models and validation rules
│   ├── scheduler.py           # Schedule CSV parsing and date matching
│   ├── state_manager.py       # Atomic state persistence for posted rows
│   ├── tool_registry.py       # Tool registry and operational handlers
│   └── trace_logger.py        # Structured JSONL telemetry logger
├── mock_social/
│   ├── __init__.py
│   ├── mock_server.py         # FastAPI mock social media server
│   ├── requirements.txt       # Dependencies for the mock service
│   └── templates/
│       ├── compose.html       # Tweet composition interface
│       └── login.html         # Session authentication interface
├── tests/
│   ├── test_browser_actor.py  # Browser actor interaction tests
│   ├── test_end_to_end.py     # Full integration pipeline tests
│   ├── test_evaluate.py       # Evaluation logic unit tests
│   ├── test_groundedness.py   # URL and mention hallucination detection tests
│   ├── test_guardrails.py     # Deterministic safety chain tests
│   ├── test_llm_schema.py     # Pydantic output model tests
│   ├── test_scheduler.py      # Scheduling and date filtering tests
│   ├── test_state_manager.py  # State persistence and recovery tests
│   ├── test_tool_registry.py  # Tool registration tests
│   └── test_traces.py         # Telemetry schema tests
├── schedule.csv               # Input posting schedule
├── evaluate.py                # Quantitative evaluation and benchmark runner
├── docker-compose.yml         # Container orchestration manifest
├── Dockerfile                 # Agent runner container definition
├── Dockerfile.mock_social     # Mock social platform container definition
├── pyproject.toml             # Project build configuration and dependencies
├── pytest.ini                 # Pytest test execution settings
└── .env.example               # Environment variables configuration template
```

## Getting Started

### Prerequisites

- Python 3.11 or later
- Docker and Docker Compose (recommended for containerized execution)
- Modern web browser drivers (managed automatically via Playwright)

### Local Environment Setup

1. **Clone the repository**

```bash
git clone https://github.com/Manirider/Guardrailed-X-Agent-Harness.git
cd Guardrailed-X-Agent-Harness
```

2. **Initialize python environment**

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
playwright install
```

3. **Configure environment settings**

```bash
cp .env.example .env
```

### Configuration Reference

Configure execution parameters via `.env`:

| Parameter | Type | Default | Description |
| :-- | :-- | :-- | :-- |
| `LLM_BASE_URL` | string | `http://mock-llm:8000/v1` | Base URL for OpenAI-compatible endpoint |
| `OPENAI_API_KEY` | string | `replace_me` | Authentication key for LLM provider |
| `MOCK_SOCIAL_URL` | string | `http://mock_social:8080` | URL of target social media interface |
| `MOCK_USERNAME` | string | `test_user` | Authentication username for target platform |
| `MOCK_PASSWORD` | string | `test_password` | Authentication password for target platform |
| `LLM_MODEL` | string | `mock-model` | Target model name for completion requests |
| `LLM_TEMPERATURE` | float | `0` | Model temperature (0 for deterministic output) |
| `HITL_ENABLED` | boolean | `false` | Gate publishing behind human approval prompt |
| `HEADLESS` | boolean | `true` | Run Playwright browser without visual UI |
| `POSTING_ENABLED` | boolean | `true` | Toggle browser publishing actions |
| `LOG_LEVEL` | string | `INFO` | Standard logging verbosity |
| `STATE_DIR` | path | `./data` | Directory for posted ID tracking and state files |

## Running the Agent

### Option 1: Docker Compose (Full Stack)

Launch both the mock social media service and the posting agent with automated healthchecks:

```bash
docker compose up --build
```

The mock social server becomes reachable at `http://localhost:8080`.

### Option 2: Local CLI Execution

Run the agent harness directly against the configured schedule:

```bash
python -m harness.cli
```

### Schedule CSV Specification

The scheduler reads `schedule.csv` using the following schema:

| Field | Format | Description |
| :-- | :-- | :-- |
| `row_id` | string | Unique primary key identifying the post record |
| `post_date` | YYYY-MM-DD | Target publication date in UTC |
| `raw_text` | string | Source content to be refined and posted |
