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
│   ├── test_tool_registry.py  # Tool registry tests
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

## Deterministic Guardrail Chain

The guardrail engine evaluates candidate text through three sequential, non-bypassable verification steps:

### 1. Hard Length Limitation
- Validates that `len(candidate_text) <= 280` characters.
- Violations append an explicit error tag (`length:<count>`) to the failure reasons.

### 2. Banned Term Inspection
- Performs token-aware regular expression scanning across configurable prohibited terms.
- Ensures words like `guarantee` or `investment` are blocked without false-positive matching on substrings.

### 3. Groundedness and Entity Preservation
- Extracts external resource links (`https?://[^\s]+`) and social mentions (`@[A-Za-z0-9_]+`) from both raw source and candidate text.
- Enforces strict entity subset matching:
  - Any URL appearing in the candidate that was not in the source triggers `introduced_url`.
  - Any mention appearing in the candidate that was not in the source triggers `introduced_mention`.

### Automated Fallback & Safety Gates

```
                    ┌───────────────────────────┐
                    │  Candidate Text Generated │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │ Guardrail Validation Run  │
                    └─────────────┬─────────────┘
                                  │
                   Pass ┌─────────┴─────────┐ Fail
                        │                   │
                        ▼                   ▼
             ┌─────────────────────┐ ┌─────────────────────┐
             │ Keep Formatted Text │ │ Fallback to Raw     │
             │ (Candidate Approved)│ │ Source Text         │
             └──────────┬──────────┘ └──────────┬──────────┘
                        │                   │
                        └─────────┬─────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │ Post-Fallback Safety Gate │
                    │ len(final_text) <= 280?   │
                    └─────────────┬─────────────┘
                                  │
                   Pass ┌─────────┴─────────┐ Fail
                        │                   │
                        ▼                   ▼
             ┌─────────────────────┐ ┌─────────────────────┐
             │ Dispatch Playwright │ │ Reject and Abort    │
             │ Publishing Action   │ │ (Error Logged)      │
             └─────────────────────┘ └─────────────────────┘
```

## Quantitative Evaluation and Metrics

The benchmark suite evaluates agent reliability using execution traces generated during production or test runs:

```bash
python evaluate.py
```

The script parses `traces.jsonl` and computes key metrics saved to `metrics.json`:

| Metric Name | Calculation Method | Target Objective |
| :-- | :-- | :-- |
| `task_completion_rate` | Distinct successful posts divided by attempted due rows | Maximized throughput without duplicate posts |
| `groundedness_score` | Proportion of evaluated LLM outputs passing groundedness checks | Elimination of ungrounded URLs and mentions |
| `guardrail_trigger_rate` | Proportion of runs where at least one safety check was activated | Accurate detection and mitigation of policy violations |

### Structured Observability Traces

Every execution generates a comprehensive audit entry in `traces.jsonl`:

```json
{
  "timestamp": "2026-10-03T14:22:10.512401+00:00",
  "run_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "row_id": "row_002",
  "post_date": "2026-10-03",
  "raw_text": "Remember to backup your data https://example.com/backup",
  "llm_text": "Always backup your data! Visit https://example.com/backup #Security",
  "guardrail_passed": true,
  "guardrail_failure_reason": null,
  "final_posted_text": "Always backup your data! Visit https://example.com/backup #Security",
  "action_status": "success",
  "fallback_used": false,
  "duration_ms": 312
}
```

## Testing and Quality Assurance

Execute the complete test suite across all subsystems:

```bash
pytest
```

The automated test suite verifies:
- **Guardrail Unit Tests**: Edge cases for character boundaries, punctuation, URL variants, and case insensitivity.
- **Scheduler Logic**: UTC date matching, future post filtering, and handling multiple due rows.
- **State Persistence**: Idempotency checks and atomic updates to prevent double-posting.
- **Evaluation Accuracy**: Mathematical validation of completion rates, groundedness ratios, and trigger frequencies.
- **End-to-End Flow**: Integration runs traversing scheduling through simulated browser dispatch.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
