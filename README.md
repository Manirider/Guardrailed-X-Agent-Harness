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
