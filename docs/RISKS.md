# Agentic Safety Layer (ASL) — Architecture Risk Register

**Version:** 0.1  
**Reviewer:** Principal Engineer review  
**Status:** Pre-build  
**Sources:** [PROJECT_BRIEF.md](./PROJECT_BRIEF.md) · [PRODUCT_SPEC.md](./PRODUCT_SPEC.md) · [ARCHITECTURE.md](./ARCHITECTURE.md) · [PLAN.md](./PLAN.md)  
**Last updated:** 2026-06-28

---

## Executive Summary

ASL's architecture is **appropriate for a solo-builder, single-tenant v1** with clear module boundaries and honest scope limits. The design correctly prioritizes NexusFlow integration over platform breadth.

The highest-severity risks cluster around three themes:

1. **Governance bypass** — trusted runtime claims, fail-mode misapplication, and policy gaps can allow destructive actions without durable audit.
2. **Sync gate fragility** — audit writes, session-context reads, and escalation polling sit on or adjacent to the latency-critical path; voice agents (OmniFlow) amplify this.
3. **Specification debt** — PRODUCT_SPEC §7 lists 30+ unresolved requirements; ARCHITECTURE resolves some via ADRs, but gaps in RBAC, rule precedence, and consistency guarantees remain build-time hazards.

**Risk count by severity:**

| Severity | Count |
|----------|-------|
| Critical | 6 |
| High | 14 |
| Medium | 18 |
| Low | 10 |

---

## 0. v0 Risk Subset

During v0 build ([PLAN.md](./PLAN.md) Phases 0–2), only these risks are actively live. The full register below applies once v0 graduates to Phase 3+ in PLAN.md.

| ID | Risk | Severity | Why live in v0 |
|----|------|----------|----------------|
| DC-01 | ALLOW returned before audit persisted | **Critical** | Core loop must write audit before response |
| SEC-01 | Policy misconfiguration allows destructive actions | **Critical** | First policy file + tool classifications ship in v0 |
| SEC-02 | Fail-mode applied incorrectly during outage | **Critical** | Global fail-mode tested manually in Phase 2 |
| TD-02 | Policy rule precedence undefined | **High** | Rule engine ships in Phase 1 |
| TD-13 | OpenAPI not yet source of truth | **Medium** | Govern contract locked in Phase 0 |
| M-01 | Solo maintainer operational load | **High** | Structural — one person building everything |
| M-10 | Scope creep toward enterprise control plane | **High** | Primary v0 failure mode is building polish before the loop |
| M-04 | Test strategy undefined | **High** | Govern + engine tests required at Phase 1 exit |

---

## Severity Definitions

| Level | Definition |
|-------|------------|
| **Critical** | Can cause unauthorized production impact, permanent audit loss, or complete governance failure with no acceptable v1 workaround |
| **High** | Significant security, reliability, or product failure under realistic conditions; requires mitigation before or during Phase 1 |
| **Medium** | Degrades experience, creates ops burden, or becomes painful at modest scale; acceptable short-term with documented mitigations |
| **Low** | Minor impact, edge case, or deferred concern aligned with explicit v1 non-goals |

---

## 1. Scaling Issues

| ID | Risk | Severity | Source | Description | Mitigation |
|----|------|----------|--------|-------------|------------|
| S-01 | Sync govern gate latency budget | **High** | PRODUCT_SPEC §6, ARCH §2.3 | Every tool call blocks on HTTP round-trip + policy eval + DB write. Target <100ms p95 is ambitious with PostgreSQL INSERT on the ALLOW path. OmniFlow voice pipeline has stricter latency needs than text agents. | In-memory policy cache (planned); consider async audit write with `decision_id` pre-allocation; benchmark early with NexusFlow tool volume; document bypass only for pre-classified READ tools if profiling fails |
| S-02 | Escalation polling amplification | **High** | ARCH §4.5, §10.1 | N blocked agents polling every 2–5s plus admin UI polling every 5s creates read load that scales with agent count × wait time, not request rate. | Exponential backoff in SDK; server-side `Retry-After` header; cap concurrent pending escalations per session; webhooks in Phase 4 |
| S-03 | Single VPS compute ceiling | **Medium** | ARCH §9.1, PROJECT_BRIEF | One Docker Compose host runs API + UI + PostgreSQL + nginx. No horizontal scaling, no redundancy. CPU saturation affects govern latency directly. | Accept for v1; monitor p95 latency; document Phase 6 HA path; keep fail-mode in runtimes |
| S-04 | PostgreSQL write throughput on audit table | **Medium** | ARCH §5.2, §10.1 | Append-only `decision_records` is the primary write path. High tool-call volume (8-agent NexusFlow, parallel subagents) can saturate a single PG instance. | Partition by month at >10M rows; batch writes (Phase 6); right-size VPS; index discipline |
| S-05 | Session context DB read on composite rules | **Medium** | ARCH §5.2, PRODUCT_SPEC B3 | Rules using `session_rejection_count` require a DB read per govern call, breaking the "no DB on ALLOW path" assumption. | Cache session context in-memory with short TTL; lazy-load only when composite rules match tool tier; document rule authoring guidance |
| S-06 | In-memory rate limiter | **Low** | ARCH §4.7 | Token bucket resets on restart; not shared across instances. Irrelevant for single-instance v1; blocks multi-instance without Redis. | Defer to Phase 6; document single-instance assumption |
| S-07 | Audit query and export at scale | **Medium** | ARCH §4.2, §5.4 | Unbounded JSONB columns + 365-day retention without partitioning makes session/time-range queries slow as log grows. | Date partitioning; retention worker (P1); limit export date ranges; read replica in Phase 6 |
| S-08 | Python single-process GIL | **Low** | ARCH §2.4 | Uvicorn workers help read concurrency but policy eval + DB writes share process resources. Unlikely bottleneck at v1 volumes. | Profile before optimizing; multiple workers with shared PG if needed |
| S-09 | Monorepo build and deploy surface | **Medium** | ARCH §3, PROJECT_BRIEF | API, admin UI, CLI, SDK, schemas, and integrations all ship from one repo. Solo maintainer deploys 3+ artifacts. | Shared CI pipeline; single `docker compose up`; pin versions in compose file |

---

## 2. Security Risks

| ID | Risk | Severity | Source | Description | Mitigation |
|----|------|----------|--------|-------------|------------|
| SEC-01 | Policy misconfiguration allows destructive actions | **Critical** | PRODUCT_SPEC §6, ARCH §10.2 | Wrong YAML rule, missing tool classification, or `default_unclassified: ALLOW` can permit DELETE/CRITICAL actions. No staging/shadow mode until Phase 4. | Default-deny or default-escalate for unclassified tools; schema validation on deploy; policy review checklist; Git-version policies; dry-run endpoint before activate |
| SEC-02 | Fail-mode applied incorrectly during outage | **Critical** | PRODUCT_SPEC §6, Journey 4, ARCH §8.4 | Runtime SDK decides ALLOW/DENY locally when ASL is unreachable. Misconfigured tier overrides or stale SDK config can fail-open on DESTRUCTIVE actions — a governance blackout becomes a security hole. | Per-tier fail-closed defaults for WRITE/DESTRUCTIVE/CRITICAL; integration tests for outage scenarios; SDK config validation on startup; loud logging when degraded |
| SEC-03 | Forged or inaccurate delegation chains | **High** | ARCH ADR-006, PRODUCT_SPEC §7 | `agent_id`, `principal`, and `delegation_chain` are self-reported by the runtime. A compromised or buggy agent can omit chain hops or misattribute principal. | Document trust model explicitly; v1 acceptable for self-hosted NexusFlow; Phase 4 signed delegation tokens; anomaly detection on chain depth |
| SEC-04 | API key leakage | **High** | PRODUCT_SPEC §6, ARCH §6 | Keys in runtime env vars, CI logs, or admin UI `sessionStorage` are high-value targets. Single admin key grants policy deploy + approval + key management. | Scoped keys per runtime; rotation CLI; never log keys; separate govern vs admin keys; CSP + no key in URL params |
| SEC-05 | Admin API key in browser sessionStorage | **High** | ARCH §6.3 | XSS in admin UI or a malicious browser extension can exfiltrate the full admin key. No short-lived tokens in v1. | Strict CSP; sanitize all rendered argument fields; HTTP-only cookie proxy in Phase 2; minimal admin UI attack surface |
| SEC-06 | No approver RBAC enforcement | **High** | PRODUCT_SPEC §7, ARCH §5.2 | `assigned_role` (team_lead, admin) is stored but architecture does not define how approver identity is authenticated or authorized against role. Any holder of `admin:write` can approve CRITICAL actions. | v1: document single-operator model; Phase 2: `admin_users` table + role binding; reject approve if `approver_id` lacks required role |
| SEC-07 | API key lookup design ambiguity | **High** | ARCH §6.2, §5.2 | Auth flow says "hash token, lookup key_hash" but bcrypt is not directly lookupable — implies O(n) scan or a design inconsistency. Performance and timing side-channels at scale. | Use HMAC-SHA256 with server pepper for lookup key; bcrypt only for storage verification; or prefix-based key IDs (`asl_live_<key_id>_<secret>`) |
| SEC-08 | PII and secrets in audit log | **High** | PRODUCT_SPEC §7, ARCH §5.3 | Redaction is pattern-based (password, email, phone). Nested PII, Indian locale fields (Aadhaar, PAN), and custom argument shapes will leak. `arguments_hash` enables offline brute-force if args are low-entropy. | Extensible redaction config; deny-list + regex; hash with per-deployment salt; audit access restricted to `audit:read`; document what ASL does not redact |
| SEC-09 | Idempotency key optional | **Medium** | ARCH §4.3 | Without `Idempotency-Key`, network retries can create duplicate decisions and, on APPROVED escalation replay, duplicate production side effects. | Make key recommended in SDK by default; server-side dedup on `(session_id, tool, arguments_hash)` within window |
| SEC-10 | Unauthenticated health endpoints | **Low** | ARCH §4.2 | `/health` and `/ready` expose operational status. Low risk for self-hosted; can aid reconnaissance. | Rate-limit; minimal response body; optional auth for `/ready` in production |
| SEC-11 | No transport security between internal services | **Medium** | ARCH §9.1 | TLS terminates at nginx; API↔PostgreSQL traffic is unencrypted inside Docker network. VPS compromise exposes audit data in transit. | Docker network isolation; PG SSL for production; VPS hardening guide |
| SEC-12 | Approval queue spam / resource exhaustion | **Medium** | ARCH §10.2 | Adversarial or runaway agent can flood pending approvals, bloating DB and admin UI. | Per-agent rate limits; max pending per session; auto-expire TTL |
| SEC-13 | Degraded-mode actions invisible to ASL | **High** | PRODUCT_SPEC F4, ARCH §8.4 | Fail-open ALLOW decisions made locally are logged only in runtime, not in ASL audit store. Compliance gap during outages. | SDK posts degraded audit batch on recovery (P1); runtime local log format spec; operator alert on circuit-breaker open |
| SEC-14 | DPDP data residency undecided | **Medium** | PRODUCT_SPEC §7 | Audit records may contain customer PII. India-region hosting requirement unresolved. Rajesh persona depends on this. | Document data flow; configurable region in Phase 5; no compliance claims in v1 |

---

## 3. Technical Debt

| ID | Risk | Severity | Source | Description | Mitigation |
|----|------|----------|--------|-------------|------------|
| TD-01 | 30+ unresolved requirements at build start | **High** | PRODUCT_SPEC §7 | Missing specs for rule precedence, approver auth, escalation protocol (partially resolved), export format, NexusFlow hook point, SDK error contract. Building without these forces rework. | Resolve P0 items in OpenAPI + policy schema before Phase 0 exit; track in ADR log |
| TD-02 | Policy rule precedence undefined | **High** | PRODUCT_SPEC §7 | Architecture shows ordered rules but no conflict resolution when multiple rules match. First-match vs highest-priority vs most-specific is unspecified. | Define and document evaluation order in policy schema v1; unit test rule conflicts |
| TD-03 | SQLite vs PostgreSQL dual support | **Medium** | PROJECT_BRIEF, ARCH §2.4 | Local dev may use SQLite; production uses PostgreSQL. JSONB, partial indexes, and array types diverge. | CI tests PostgreSQL only; SQLite dev-only with explicit "not supported for production" |
| TD-04 | In-process event bus | **Medium** | ARCH §8.1 | `DecisionMade` → Audit Service via asyncio callbacks. Process crash between decision response and event handler loses audit record if async write fails. | Synchronous audit write for ESCALATE; transactional outbox pattern for ALLOW if async; integration tests for crash recovery |
| TD-05 | Polling chosen for escalation (ADR-002) | **Medium** | ARCH ADR-002 | Defers webhooks, SSE, long-poll. Every integrator reimplements poll loop. Becomes migration tax when upgrading. | SDK abstracts polling; stable `poll_url` contract; webhook additive in Phase 4 |
| TD-06 | No policy shadow/dry-run mode | **Medium** | PRODUCT_SPEC §7, Phase 4 | Operators cannot test policy v4 against live traffic before activation. Rollback is reactive, not preventive. | `POST /policies/validate` with sample requests; shadow mode in Phase 4; staging policy pointer |
| TD-07 | Phase ordering inconsistency | **Medium** | PRODUCT_SPEC vs ARCH | OmniFlow is P1 in spec but Phase 3 in roadmap. Admin UI is P1 but Phase 2. Risk of building wrong priority. | Align phase gates with P0/P1 labels; NexusFlow first, no exceptions |
| TD-08 | Trusted identity model (ADR-006) | **High** | ARCH ADR-006 | Deferring agent registry and signed chains is correct for v1 but embeds a trust assumption that will be expensive to retrofit. | Version request schema; design `schema_version` field now; plan signed chain format without implementing |
| TD-09 | TTL worker reliability | **Medium** | ARCH §3, §7.2 | Background worker expires approvals. If worker stops, stale PENDING records accumulate; agents hang until client timeout. | Run worker in same process with health metric; stale-approval alert; agent-side timeout mandatory |
| TD-10 | Monolith extraction seams untested | **Low** | ARCH §2.2 | Module boundaries (engine/, domain/, api/) are documented but unenforced until package linting or import rules exist. | Import linter (e.g., import-linter); engine unit tests with zero I/O |
| TD-11 | Observability deferred to P1 | **Medium** | ARCH Appendix B | No metrics, tracing, or alerting in Phase 0. Operating blind during first NexusFlow integration. | Minimum viable metrics in Phase 0: `decision_latency`, `pending_approvals`, error rate |
| TD-12 | Hash chain / tamper evidence deferred to Phase 4 | **Medium** | PRODUCT_SPEC E6 | Append-only via app layer is not tamper-evident. DBA or compromised API process can UPDATE/DELETE despite intent. | DB role permissions (INSERT+SELECT only); consider pg_audit; hash chain when Rajesh persona matters |
| TD-13 | OpenAPI not yet source of truth | **Medium** | ARCH §4.1, PRODUCT_SPEC Phase 0 | `asl-schemas/openapi/asl-v1.yaml` is planned but empty. Contract drift between SDK, integrations, and server is likely. | Generate server models from OpenAPI; contract tests in CI |
| TD-14 | Fail-mode config in two places | **Medium** | ARCH §7.1 | Fail-mode exists in policy YAML and runtime SDK config. Divergence causes unpredictable outage behavior. | SDK fetches fail-mode from ASL on startup; single source in `system_config`; cache with TTL |

---

## 4. UX Risks

| ID | Risk | Severity | Source | Description | Mitigation |
|----|------|----------|--------|-------------|------------|
| UX-01 | Agent hangs during ESCALATE | **High** | PRODUCT_SPEC Journey 1, ARCH §4.5 | Agent blocks on poll loop waiting for human. Default 300s TTL with 2–5s polls ties up agent threads/workers. Multi-agent orchestration compounds waits. | Document async escalation pattern; agent timeout < approval TTL; cancel tool plan on EXPIRED; queue position in poll response |
| UX-02 | Voice pipeline latency unacceptable | **High** | PRODUCT_SPEC §7, Journey 5 | OmniFlow CRM updates through sync HTTP gate add hundreds of ms — unacceptable in live voice conversation. | Pre-approve session scopes; cache ALLOW for idempotent READ; local allowlist for voice-safe tools; measure before Phase 3 |
| UX-03 | No escalation notifications | **High** | PRODUCT_SPEC C6, Phase 4 | Operator must poll admin UI or CLI to discover pending approvals. Solo builder may miss approvals; agents wait full TTL. | Email/webhook minimum for P1 on-call; browser notifications in admin UI; Slack hook in Phase 4 |
| UX-04 | Admin API key entry UX | **Medium** | ARCH §6.3 | Operator pastes long-lived admin key into browser on first visit. No rotation reminder, no key expiry, no logout UX spec. | Key creation onboarding in README; logout clears sessionStorage; display key fingerprint not full key |
| UX-05 | Approval context insufficient for fast decisions | **Medium** | PRODUCT_SPEC D2 | Approver must judge tool, args, delegation chain, risk tier, and principal in minimal UI. Missing diff view, prior session actions, or tool description. | Approval detail page shows chain visualization; link to session audit; tool metadata from policy |
| UX-06 | Concurrent approval conflict (409) | **Medium** | PRODUCT_SPEC §7, ARCH §5.2 | Two operators approve same item; second gets 409. UI optimistic update may show false success. | Clear conflict message; refetch on 409; show "resolved by X" state |
| UX-07 | Mobile approval not supported | **Medium** | PRODUCT_SPEC §7 | On-call approver cannot act from mobile. Responsive admin UI not specified. | Responsive approval queue; PWA consideration for Phase 2 |
| UX-08 | DENY reason not actionable for agent | **Medium** | PRODUCT_SPEC C2 | Agent receives `reason_code` but no structured guidance for recovery or user messaging. | Standard reason code catalog; document agent handling per code |
| UX-09 | Audit viewer overwhelm | **Low** | PRODUCT_SPEC E2 | High-volume sessions produce unpaginated-feeling tables. Filters exist in API but UX for incident reconstruction is unspecified. | Session timeline view; default 24h window; export for deep analysis |
| UX-10 | Policy editing requires YAML expertise | **Medium** | PROJECT_BRIEF, PRODUCT_SPEC G5 | Arjun persona is comfortable with YAML; Rajesh is not. Phase 5 visual editor is far out. | Example policies; `validate` CLI with clear errors; policy authoring doc |
| UX-11 | Fail-mode behavior confusing to end user | **Medium** | Journey 4 | When ASL is down, agent may proceed (READ) or block (DESTRUCTIVE) without user-visible explanation. | Runtime surfaces degraded mode to user; consistent error copy |

---

## 5. Data Consistency Risks

| ID | Risk | Severity | Source | Description | Mitigation |
|----|------|----------|--------|-------------|------------|
| DC-01 | ALLOW returned before audit persisted | **Critical** | ARCH §2.3, §10.1 | Sequence diagram shows API responds 200 then audit INSERT. If async write fails or process crashes, production action executes with no audit record — violates North Star metric. | Synchronous INSERT before response for all outcomes; or two-phase: allocate `decision_id`, insert, then respond; retry with idempotency |
| DC-02 | ESCALATE multi-step without transaction | **High** | ARCH §8.2 | `decision_record` INSERT and `approval_request` INSERT are separate. Partial failure leaves decision without approval or approval without decision. | Single DB transaction for govern path; rollback on any failure; return 503 on partial state |
| DC-03 | Policy activation vs in-memory cache race | **High** | ARCH §7.3 | Activate in DB then swap memory pointer. Requests in flight may evaluate against old policy while audit records new version, or vice versa. | Version stamp on request entry; atomic pointer swap; brief drain or version check at eval start |
| DC-04 | Session context lost update race | **Medium** | ARCH §5.2 | `rejection_count` increment is read-modify-write. Concurrent DENY decisions in same session can under-count. | `UPDATE ... SET rejection_count = rejection_count + 1`; or serializable isolation for session row |
| DC-05 | Idempotency dedup race | **Medium** | ARCH ADR-007 | Two identical requests with same `Idempotency-Key` arriving concurrently can both evaluate policy before either INSERT completes. | Unique constraint on `idempotency_key` + `ON CONFLICT RETURNING existing`; transactional dedup check |
| DC-06 | Approval APPROVED after agent timeout | **High** | ARCH §4.5, §7.2 | Human approves at 4:59; agent timed out at 4:30 and aborted. Approval is orphaned; audit shows APPROVED but action never ran — or agent already moved on and retries cause duplicate execution. | Include `execution_token` valid only before agent timeout; approval response includes `agent_must_retry`; idempotent tool execution guidance |
| DC-07 | Fail-mode local decisions never reconciled | **High** | SEC-13, Journey 4 | Outage period creates audit gap. No backfill path when ASL recovers. Compliance timeline has holes. | SDK buffers degraded decisions; `POST /audit/degraded` batch ingest on recovery |
| DC-08 | `decision_records.outcome` static after escalation resolves | **Medium** | ARCH §8.2 | Initial record says ESCALATE; resolution is in separate tables. Querying audit by outcome=ESCALATE includes resolved items unless joined. | Add `final_outcome` column or materialized view; document query patterns |
| DC-09 | Clock skew on client `timestamp` | **Medium** | ARCH §4.3 | Request carries client-supplied `timestamp`. Malicious or drifted clients affect ordering and TTL calculations. | Treat server `received_at` as authoritative; validate client timestamp within ±5min window |
| DC-10 | Audit export job orphan artifacts | **Low** | ARCH §5.1 | `AUDIT_EXPORT_JOB` writes to filesystem. Job failure leaves partial files; retention worker may race. | Atomic write to temp path then rename; job status machine; cleanup on failure |
| DC-11 | Policy version FK not enforced on rollback | **Medium** | ARCH §5.2 | `policy_version` on decisions references version string. Rollback activates old version; FK remains valid but semantic "active at decision time" requires immutable version records. | Never delete policy versions; `is_active` flag only |
| DC-12 | No distributed consistency model | **Low** | ARCH §9.7 | Single instance avoids split-brain. Documented for Phase 6. | Explicit single-writer assumption in v1 docs |

---

## 6. Maintainability Concerns

| ID | Risk | Severity | Source | Description | Mitigation |
|----|------|----------|--------|-------------|------------|
| M-01 | Solo maintainer operational load | **High** | PROJECT_BRIEF | One person owns policy authoring, infra, integrations (NexusFlow, OmniFlow), admin UI, CLI, SDK, and on-call approvals. Burnout risk is structural. | CLI over UI; YAML over visual editor; minimize deploy steps; defer Phase 4+ explicitly |
| M-02 | Integration sprawl across runtimes | **High** | ARCH §3, PRODUCT_SPEC H | Each runtime needs a hook maintaining request schema, fail-mode, and poll logic. Schema changes require N integration updates. | `asl-client` SDK as single integration surface; contract tests; semver on `asl-schemas` |
| M-03 | Policy schema evolution | **Medium** | PRODUCT_SPEC §7, Phase 0 | `schema_version` in policy YAML but no migration tooling for policy document upgrades across ASL versions. | Policy migrator CLI; support N and N-1 schema versions; validate on deploy |
| M-04 | Test strategy undefined | **High** | ARCH §3 | Folder structure has `tests/unit`, `integration`, `e2e` but no testing requirements in spec. Governance bugs are high-impact. | Minimum: engine unit tests, govern API integration tests, fail-mode e2e, outage simulation |
| M-05 | Documentation drift across three docs | **Medium** | All | PROJECT_BRIEF, PRODUCT_SPEC, and ARCHITECTURE can diverge (e.g., OmniFlow priority, admin UI phase). | Single ADR log; RISKS.md cross-references; update all docs on phase changes |
| M-06 | Alembic migration discipline | **Medium** | ARCH §3 | Schema changes to append-only tables need careful migrations. Mistakes can break immutability guarantees. | Migration review checklist; no DROP on decision_records; staging DB for migration test |
| M-07 | Dependency and supply chain | **Low** | PROJECT_BRIEF | FastAPI, React, PostgreSQL, nginx — standard stack. Python agent ecosystem deps change frequently. | Pin versions in pyproject.toml and package-lock; Dependabot; minimal dependencies |
| M-08 | Backup RPO 24 hours | **Medium** | ARCH §9.6 | Daily `pg_dump` means up to 24h audit loss on catastrophic failure. Unacceptable if compliance is a driver. | Increase backup frequency before Rajesh persona; WAL archiving guide |
| M-09 | Competitive convergence with ACP | **Low** | PRODUCT_SPEC Appendix | ACP uses same `/govern/tool-use` pattern. Differentiation requires execution quality, not just API shape. | Focus on risk taxonomy depth, audit UX, self-host simplicity |
| M-10 | Scope creep toward enterprise control plane | **High** | PRODUCT_SPEC §6, PROJECT_BRIEF | SSO, multi-tenant, framework adapters, visual policy editor, and HA are all tempting mid-build. Solo team cannot sustain. | Enforce non-goals in PR review; Phase 6 gate explicit |
| M-11 | Engine purity boundary erosion | **Medium** | ARCH §3 | `engine/` must stay I/O-free. Pressure to add DB-backed session context or logging will couple policy logic to infrastructure. | Import linter; code review rule; keep context injection at service layer |
| M-12 | Admin UI maintenance burden vs CLI | **Medium** | PROJECT_BRIEF | React SPA requires frontend toolchain, npm audit, and UI testing. CLI may suffice for Arjun persona indefinitely. | Ship CLI-first; minimal admin UI scope; shared OpenAPI-generated client |

---

## 7. Cross-Cutting Risk Matrix

Risks that span multiple categories:

| Theme | IDs | Combined Severity | Notes |
|-------|-----|-------------------|-------|
| **Governance bypass** | SEC-01, SEC-02, SEC-03, SEC-13, DC-07 | **Critical** | Policy gaps + outage behavior + untrusted claims can allow unaudited production impact |
| **Audit completeness** | DC-01, DC-02, SEC-13, DC-07, TD-04 | **Critical** | North Star metric (100% audited actions) is architecturally at risk on ALLOW path and during outages |
| **Escalation path fragility** | S-02, UX-01, UX-03, DC-06 | **High** | Polling + no notifications + timeout races create unreliable HITL |
| **Spec → build gap** | TD-01, TD-02, TD-13, M-04 | **High** | Unresolved requirements and missing tests multiply rework cost |
| **Solo team sustainability** | M-01, M-10, S-09, UX-10 | **High** | Architecture is sound but operationally heavy for one person |

---

## 8. Pre-Build Gate Checklist

### v0 gate (must resolve before writing the govern endpoint)

| # | Item | Risk IDs | Status |
|---|------|----------|--------|
| 1 | OpenAPI contract for `POST /govern/tool-use` (informal OK; full publish tooling not required) | TD-13, M-02 | Open |
| 2 | Policy rule precedence documented | TD-02 | Open |
| 3 | Govern path audit write is synchronous | DC-01 | Open |
| 4 | Default unclassified tool behavior = ESCALATE or DENY | SEC-01 | Open |
| 5 | API key lookup design finalized (HMAC/prefix or single env key for v0) | SEC-07 | Open |

### v1 gate (resolve before Phase 3 of the full plan — operability and beyond)

| # | Item | Risk IDs | Status |
|---|------|----------|--------|
| 1 | OpenAPI v1 published and contract-tested (full CI) | TD-13, M-02 | Open |
| 2 | ESCALATE path wrapped in DB transaction | DC-02 | Open |
| 3 | Fail-mode single source of truth | TD-14, SEC-02 | Open |
| 4 | SDK generates Idempotency-Key by default | SEC-09, DC-05 | Open |
| 5 | Engine unit tests + govern integration tests exist | M-04 | Open |
| 6 | Outage simulation test for fail-mode | SEC-02, SEC-13 | Open |
| 7 | Degraded audit backfill API designed | DC-07, SEC-13 | Open |
| 8 | Agent timeout vs approval TTL interaction documented | DC-06, UX-01 | Open |

---

## 9. Recommended Mitigation Priority

### Before Phase 0 exit (blocking)

1. **DC-01** — Synchronous audit write before govern response
2. **SEC-01** — Default-deny/escalate for unclassified tools
3. **TD-02** — Rule precedence specification
4. **SEC-07** — API key lookup design
5. **TD-13** — OpenAPI as contract source of truth

### During Phase 1 (NexusFlow)

6. **SEC-02** — Fail-mode integration tests
7. **DC-02** — Transactional ESCALATE path
8. **UX-01** — Agent timeout semantics
9. **M-04** — Test suite for govern + policy engine
10. **TD-11** — Minimum metrics

### Before Phase 2 (Admin UI + delegation)

11. **SEC-06** — Approver authorization model
12. **UX-03** — Escalation notification (email minimum)
13. **DC-06** — Approval vs agent timeout coordination
14. **SEC-05** — Admin UI security hardening

### Before Phase 3 (OmniFlow)

15. **S-01, UX-02** — Latency profiling and voice-specific patterns
16. **DC-07** — Degraded audit backfill

---

## 10. Accepted Risks (v1 Non-Goals)

These risks are **consciously accepted** per PROJECT_BRIEF non-goals and ARCHITECTURE v1 scope. Revisit when entering Phase 5/6.

| Risk ID | Acceptance Rationale |
|---------|---------------------|
| S-03, S-06 | Single VPS, single instance — aligned with self-host budget |
| SEC-03, TD-08 | Trusted runtime for delegation — self-hosted NexusFlow is sole consumer |
| TD-05 | Polling for escalation — simplicity over scale |
| TD-06 | No shadow mode — rollback sufficient for v1 |
| SEC-10 | Public health endpoint — standard practice |
| M-09 | Competitive overlap with ACP — execution differentiation |
| DC-12 | No HA consistency — Phase 6 gate |

---

## 11. Document Traceability

| This Register | Traced From |
|---------------|-------------|
| Scaling (S-*) | ARCH §2.3, §4.5, §9, §10.1; PRODUCT_SPEC §6 Technical; PROJECT_BRIEF Constraints |
| Security (SEC-*) | ARCH §5.3, §6, §10.2; PRODUCT_SPEC §6, Journey 4, §7 Identity/Delegation |
| Technical Debt (TD-*) | ARCH ADRs, §7–8; PRODUCT_SPEC §7, §8 Phases |
| UX (UX-*) | PRODUCT_SPEC Journeys 1–5, §7 HITL; ARCH §4.5, §6.3, §7.4 |
| Data Consistency (DC-*) | ARCH §2.3, §5.2, §7–8; PRODUCT_SPEC E1, F4 |
| Maintainability (M-*) | PROJECT_BRIEF Team/Constraints; ARCH §3; PRODUCT_SPEC §6 Product |

---

*This register should be reviewed at each phase exit gate and updated when ADRs are superseded or risks are mitigated.*
