# Guardrailed X Posting Agent Harness

Deterministic agent harness for scheduled social media posting with Playwright, Pydantic validation, and deterministic guardrails.

## Problem
God-prompt architectures give the LLM control over scheduling, safety, and browser actions, leading to ungrounded outputs and silent failures.

## Solution
Python owns control flow, scheduling, safety, and state. LLM is a narrow text transformation service validated by Pydantic and deterministic guardrails.

## Architecture
CSV → Scheduler → State → LLM → Pydantic → Guardrails → Fallback → HITL → Playwright → Mock Social → Trace → Metrics

## Setup
cp .env.example .env

## Docker
docker compose up --build

## Running
python -m harness.cli

## Testing
pytest

## Evaluation
python evaluate.py

## Metrics
task_completion_rate, groundedness_score, guardrail_trigger_rate
