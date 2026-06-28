# Agentic Safety Layer (ASL)

## Problem

Organizations running multiple AI agents across multiple frameworks have no single, durable, policy-driven place to decide whether an agent action should run, no independent record of that decision, and no way to update policy without touching every agent's source code.

Framework-native human-in-the-loop (HITL) solves pause-and-ask for a single agent in a single framework. It does not solve:

- **Cross-framework enforcement** — LangChain HITL does not govern a custom Groq agent or a voice pipeline's tool calls
- **Multi-hop delegation governance** — identity, scope, and audit fragment when orchestrators delegate to subagents
- **Durable, queryable audit** — no framework-agnostic record of who approved what, when, under which policy version
- **Graduated, risk-tiered policy** — binary per-tool gates without composite risk scoring, fail-mode policy, or tiered approver routing

ASL addresses this by providing a lightweight, self-hostable policy and audit layer that sits **outside** any agent runtime and gates actions before they reach production systems.

## Target Users

**Primary (v1):**
- Solo developers and small teams running custom or multi-framework agent stacks who need governance without enterprise control-plane pricing
- The builder themselves — NexusFlow (custom Groq 8-agent system) and future OmniFlow voice-agent tool calls (CRM, ticketing)

**v0 has exactly one user: the builder.** Multi-user and team framing below is aspirational context for the target product shape, not a v0 build target.

**Secondary (future):**
- Indian SMBs operating under DPDP who need audit primitives that voice/agent vendors do not provide out of the box
- Teams migrating between agent frameworks who need compliance history that survives the migration

## Core Features

- **HTTP enforcement gate** — Single `/govern/tool-use`-style endpoint that any agent calls before executing a sensitive action; returns allow, deny, or escalate
- **Risk taxonomy and policy engine** — Granular classification (READ / WRITE / DESTRUCTIVE / CRITICAL) with composite rules over tool + arguments + agent identity + session history
- **Human-in-the-loop escalation** — Risk-tiered approval workflows that route actions to appropriate approvers when policy requires it
- **Delegation-chain context** — Normalized request carrying caller identity, on-behalf-of chain, and scope across multi-hop agent delegation
- **Durable audit trail** — Framework-independent, queryable log of every decision: who approved what, when, under which policy version
- **Fail-mode policy** — Configurable fail-open vs. fail-closed behavior when the governance layer itself is unavailable
- **Self-hostable deployment** — Runs on your own infrastructure with no vendor lock-in

### v0 Definition of Done

v0 is done when: one NexusFlow tool call hits a real `/govern/tool-use` endpoint, gets classified by risk tier, returns ALLOW/DENY/ESCALATE, writes a durable audit record to PostgreSQL, and — for ESCALATE — I can approve or reject it from a terminal script and the agent resumes correctly. No UI. No CLI tool. No SDK package. No second consumer. Everything else in this brief is the target shape for *after* v0 proves the loop is useful.

## Non Goals

- Competing head-to-head with Galileo Agent Control, Kore.ai AMP, or full enterprise control-plane platforms on day one
- Shipping connectors to seven major agent frameworks (LangGraph, CrewAI, AutoGen, Google ADK, etc.) in v1 — start with own agents, add adapters incrementally
- Replacing framework-native HITL inside a single-framework, single-agent setup where built-in guardrails are sufficient
- Building a full agent orchestration runtime, observability platform, or cost-attribution suite
- Multi-tenant SaaS, billing, or enterprise SSO in v1
- DPDP compliance certification or legal advisory — provide audit primitives, not legal guarantees

## Success Metrics

*The metrics below describe the eventual system. v0 only needs to satisfy **Enforcement works end-to-end** and **Audit is queryable and complete** for the single NexusFlow case.*

- **Enforcement works end-to-end** — NexusFlow tool calls pass through ASL gate; denied actions never reach production APIs
- **Policy updates without redeploy** — Changing a rule (e.g., escalate all DESTRUCTIVE actions) takes effect without modifying agent source code
- **Audit is queryable and complete** — Every gated decision is logged with policy version, caller context, and outcome; retrievable by session, agent, or time range
- **Second consumer integrated** — OmniFlow voice-agent tool calls use the same gate and audit store as NexusFlow
- **Delegation context preserved** — Multi-hop calls record who initiated the chain and on whose behalf, not just the immediate caller
- **Fail-mode behaves as configured** — Verified fail-open and fail-closed paths when ASL is unreachable
- **Self-host cost stays low** — Runs on a single VPS or local Docker stack without paid enterprise dependencies

## Tech Stack

Frontend:
- Minimal admin UI (policy editor, audit log viewer, pending approvals queue) — React or plain HTML for v1
- Optional: CLI for policy deploy and audit queries

Backend:
- Python + FastAPI (aligns with agent ecosystem, fast to iterate solo)
- Policy engine as versioned YAML/JSON rules evaluated at request time

Database:
- PostgreSQL for audit log, policy versions, and approval records (SQLite acceptable for local dev)

Hosting:
- Docker Compose for self-hosting on a VPS (e.g., Hetzner, DigitalOcean, or local)
- No managed cloud dependency required for v1

## Constraints

Budget: ₹0–₹15,000/month (~$0–$180/month) for self-hosted infra; ₹0 if running locally or on existing hardware

Timeline: No deadline — iterative, build what is needed for NexusFlow and OmniFlow first

Team: Only me — scope must stay lean; prefer boring, proven tools over ambitious platform builds
