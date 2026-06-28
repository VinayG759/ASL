# ASL — Product Design UX Audit

**Version:** 0.1  
**Auditor lens:** Principal Product Designer (Stripe · Linear · Vercel · Intercom)  
**Scope:** Product design — information architecture, navigation, workflows, screen hierarchy, enterprise SaaS patterns. Not visual design.  
**Artifacts reviewed:** [PROJECT_BRIEF.md](./PROJECT_BRIEF.md) · [PRODUCT_SPEC.md](./PRODUCT_SPEC.md) · [ARCHITECTURE.md](./ARCHITECTURE.md) · [PLAN.md](./PLAN.md) · [RISKS.md](./RISKS.md)  
**Status:** Pre-build — **not a current build spec**  
**Build gate:** [PLAN.md Phase 6](./PLAN.md) — admin UI only if `scripts/approve.py` becomes the actual daily bottleneck. **That gate has not opened.**  
**Last updated:** 2026-06-28

---

> ⚠️ **This document does not describe anything to build right now.**
>
> Current state: v0 approval is a terminal script (`scripts/approve.py`), per
> [PROJECT_BRIEF.md](./PROJECT_BRIEF.md)'s v0 Definition of Done. No Console, no
> Inbox, no admin SPA exists or is being built.
>
> This audit becomes actionable only when [PLAN.md](./PLAN.md) Phase 6 gate opens —
> i.e., when script-based approval has become a real, felt bottleneck in actual use,
> not on a schedule and not by default. Until then, this is a reference for what the
> Console *should* look like when that day comes, written while the thinking is fresh.
>
> Do not let this document's specificity create pressure to start building toward it
> ahead of Phase 6. See [RISKS.md](./RISKS.md) M-10 ("scope creep toward enterprise
> control plane") and [PLAN.md](./PLAN.md) Plan Principle 6 ("prove the loop before
> polishing the loop").

---

## 0. Build Gate — Read Before Building Anything Below

> **Everything from §1 onward describes Phase 6+ target state. It is not actionable during v0 (Phases 0–2) or Phases 3–5 unless the Phase 6 gate in [PLAN.md](./PLAN.md) opens.**

During active build, operator workflows are API + terminal only. [PLAN.md](./PLAN.md) explicitly gates the admin UI behind Phase 6, which itself only opens if *"script-based approval has become the actual bottleneck in daily use"* — a condition that **has not occurred yet**. The full IA, navigation, screen hierarchy, workflows, and UX issue register below are **preserved design thinking for later**, not a spec to implement now.

| Current build (per [PLAN.md](./PLAN.md)) | This document |
|------------------------------------------|---------------|
| **Phases 0–2 (v0):** Govern API + `scripts/approve.py` | Full admin Console (5-item nav, Inbox, Audit, Policy, Settings) |
| **Phase 3:** CLI (`asl audit`, `asl policy`) — no UI | P0–P3 screen priorities, 23 UX issues — design backlog |
| **Phase 6 gate:** **not met** | Phase 6 deliverable spec **if and when** gate opens |

**Do not** trim, implement, or reprioritize §3–§12 during v0. Revisit this file only when the Phase 6 gate condition is met in daily use.

---

## Executive Summary

ASL has a **strong backend product thesis** — external governance, versioned policy, durable audit — but the **operator-facing product surface is under-specified and chronically deferred**. The documented admin UI (Approvals, Audit, Policy) is a feature list, not a product system. Critical operator jobs — triage escalations, reconstruct incidents, change policy safely, understand system health — lack coherent navigation, cross-linking, and notification paths.

**Verdict:** The product is architected like an API (correct for integrators) but not yet designed like an operator console (required for HITL and compliance personas). v0's script-based approval is the right engineering tradeoff; it is the wrong long-term product experience for anyone beyond a solo builder at a terminal. **The gaps catalogued below are Phase 6+ target-state design — not v0 build priorities.**

**Top 5 product design gaps:**

| # | Gap | Impact |
|---|-----|--------|
| 1 | No **triage-first** approval experience | Escalations go undiscovered; agents hang (UX-01, UX-03) |
| 2 | Audit and approvals are **siloed resources**, not linked investigation surfaces | Incident reconstruction requires mental joins across tools |
| 3 | Policy lifecycle has **no safe operator workflow** (draft → validate → activate → rollback) | Misconfiguration is the highest-impact user error |
| 4 | **No operational home** — health, queue depth, recent denials, active policy version | Operators lack situational awareness |
| 5 | Persona divergence (Arjun / Priya / Rajesh / Dev) is documented but **not reflected in IA or entry paths** | Future UI will serve nobody well |

---

## 1. Product Context & Design Maturity

### What exists today (documented)

| Surface | v0 | v1 target | Operator jobs covered |
|---------|----|-----------|-------------------------|
| `scripts/approve.py` | ✓ | Fallback | List pending, approve/reject |
| CLI (`asl audit`, `asl policy`) | Deferred (Phase 3) | ✓ | Query audit, deploy policy |
| Admin SPA (3 pages) | Deferred (Phase 6, gated) | Partial | Approvals, audit browse, policy read |
| OpenAPI / integration docs | Phase 0 | ✓ | Integrator onboarding |
| Policy YAML + file reload | v0 | ✓ | Policy authoring (developer-only) |

### Design maturity scorecard

| Dimension | Score | Notes |
|-----------|-------|-------|
| API contract clarity | Strong | Govern request/response well specified |
| Operator IA | Weak | Three pages listed; no hierarchy, no cross-links |
| Workflow completeness | Partial | Happy paths documented; edge cases in RISKS.md |
| Persona-to-surface mapping | Missing | Four personas; one undifferentiated admin UI |
| Enterprise SaaS patterns | Absent | No RBAC UX, no audit export workflow, no settings model |
| Onboarding / time-to-first-value | Underspecified | Docker + YAML; no guided setup path |

---

## 2. User Model & Mental Models

### Personas → Primary jobs → Expected product metaphor

| Persona | Primary job | Mental model | Best reference product |
|---------|-------------|--------------|--------------------------|
| **Arjun** (solo builder) | Gate tools, approve quickly, change policy | "My control panel" | Vercel dashboard (project ops) + Stripe logs |
| **Priya** (team lead) | Triage escalations, incident review, delegate approvals | "Security inbox + audit trail" | Linear Inbox + Intercom Inbox |
| **Rajesh** (compliance SMB) | Export proof, answer "who approved what" | "Compliance record system" | Stripe ReportsGlow reports + audit export |
| **Dev** (integrator) | Wire HTTP gate in <1 hour | "API + docs" | Stripe API reference |

### Conflicting mental models (design tension)

1. **Arjun** wants speed and minimal UI — CLI-first is correct.
2. **Priya** needs shared, assignable approval queues — requires inbox semantics and notifications.
3. **Rajesh** needs export and read-only audit — should never see YAML or API keys.
4. **Dev** should never need the admin UI — docs and OpenAPI are the product.

**Recommendation:** Design two product surfaces, not one:

- **Console** (operators): Triage, audit, policy lifecycle, settings
- **Developer Hub** (integrators): API reference, SDK, fail-mode guide, integration examples

Do not collapse Dev and Rajesh into the same admin SPA without role separation.

---

## 3. Information Architecture

### 3.1 Current IA (as documented)

```
Admin UI (flat, 3 pages)
├── Approvals      → pending queue
├── Audit          → decision log table
└── Policy         → active policy display (read-only in v1)
```

**Problems:**

- Flat structure treats all objects as equal-weight pages
- No **object detail** routes specified (`/approvals/:id`, `/audit/:decision_id`, `/policies/:version`)
- No **Settings** or **Integrations** domain
- No global **Search** (session ID, decision ID, agent ID)
- Policy management split across CLI, YAML files, and read-only UI — three sources of truth from the operator's perspective

### 3.2 Recommended IA (v1 target)

Organize around **operator jobs**, not backend services:

```
ASL Console
│
├── Home (Operational Overview)                    ← NEW — missing from spec
│   ├── Pending approval count + oldest item age
│   ├── Decisions last 24h (allow/deny/escalate)
│   ├── Active policy version + last changed
│   └── System status (health, fail-mode mode)
│
├── Inbox (Approvals)                              ← Rename from "Approvals"
│   ├── Pending                                    [default view]
│   ├── Resolved (approved / rejected / expired)
│   └── Approval Detail                            ← NEW — UX-05
│       ├── Action summary (tool, args, risk tier)
│       ├── Principal + delegation chain
│       ├── Session context (link → Audit filtered by session)
│       ├── Policy rule matched + version
│       └── Approve / Reject (+ reason)
│
├── Audit (Decisions)
│   ├── Timeline (default: last 24h)               ← UX-09
│   ├── Filters: session, agent, runtime, outcome, risk, policy version
│   ├── Decision Detail
│   │   ├── Full request context (redacted args)
│   │   ├── Approval resolution (if escalated)
│   │   └── Related decisions (same session)
│   └── Export                                       ← Rajesh persona (P1)
│
├── Policy
│   ├── Active (read-only summary in v1)
│   ├── Versions (list + diff)                       ← Phase 4+
│   ├── Validate (paste/upload → preview)            ← UX-10 mitigation
│   └── Activate / Rollback (with confirmation)      ← Stripe-style deploy
│
├── Integrations (read-only v1)                      ← NEW
│   ├── Connected runtimes (NexusFlow, OmniFlow)
│   ├── API key scopes (govern vs admin)
│   └── Health / latency notes
│
└── Settings
    ├── API keys (create, revoke, scopes)
    ├── Fail-mode configuration
    ├── Approval TTL defaults
    ├── Notification channels (webhook, email)       ← UX-03
    └── Retention & export schedule
```

### 3.3 Object taxonomy

| Object | Primary home | Secondary surfaces | Key relationships |
|--------|--------------|-------------------|-------------------|
| **Approval request** | Inbox | Home (count), Audit (linked) | 1:1 with decision record |
| **Decision record** | Audit | Inbox (if escalated), Policy (rule trace) | N:1 session, N:1 agent |
| **Policy version** | Policy | Audit (filter), Approval detail | Immutable; one active |
| **Session** | Audit (filter/group) | Approval detail | Aggregates decisions |
| **Agent** | Audit (filter) | Integrations | Claimed identity |
| **Principal** | Approval detail, Audit | — | End-user on whose behalf |
| **API key** | Settings | Integrations | Scoped credentials |

### 3.4 Cross-linking rules (critical for investigation UX)

Every surface should answer "where do I go next?" without copy-pasting IDs:

| From | Link to | Pattern (reference) |
|------|---------|---------------------|
| Approval detail | Session audit timeline | Intercom conversation → user history |
| Approval detail | Active policy rule | Stripe event → rule/source |
| Audit decision | Approval resolution | Linear issue → activity |
| Audit decision | Same-session siblings | Vercel deployment → build logs |
| Home alert | Filtered Audit view | Stripe Dashboard → filtered events |
| Policy version | Decisions under that version | Vercel deployment → runtime logs |

---

## 4. Navigation Structure

### 4.1 Primary navigation (recommended)

**Pattern:** Linear-style left rail — 5 items max, job-oriented labels.

```
[Logo] ASL

● Home
◆ Inbox          (badge: pending count)
▤ Audit
⚙ Policy
⋯ Settings
```

- **Inbox** not "Approvals" — signals triage responsibility (Intercom/Linear)
- **Badge on Inbox** — only persistent notification affordance until push/email ships
- **Policy** separated from **Settings** — policy is a daily object; settings are infrequent (Stripe separates "Developers" from account settings)

### 4.2 Secondary navigation (contextual)

| Context | Sub-nav or tabs |
|---------|-----------------|
| Inbox | Pending · Resolved · Expired |
| Audit | Timeline · By session · By agent · Export |
| Policy | Active · History · Validate |
| Settings | Keys · Fail-mode · Notifications · Retention |

### 4.3 Global affordances

| Affordance | Purpose | Reference |
|------------|---------|-----------|
| **Command palette** (⌘K) | Jump to session, decision ID, approval ID | Linear |
| **Global search** | Session ID, agent ID, tool name | Stripe Dashboard search |
| **Status indicator** | ASL health in header | Vercel status dot |
| **Policy version chip** | Always visible: `Policy v3` → click to Policy | Vercel env badge |

### 4.4 What v0/v1 should NOT build in nav

- Multi-tenant org switcher (non-goal)
- Framework adapter marketplace
- Visual rule builder (Phase 5+)
- Full RBAC admin (document single-operator mode first)

---

## 5. Screen Hierarchy

### 5.1 Screen map (priority order)

```
P0 — Required for HITL product viability (Phase 6 gate)
├── Auth gate (API key entry)
├── Inbox — Pending list
├── Inbox — Approval detail
└── Audit — Filtered timeline

P1 — Required for Priya/Rajesh personas
├── Home — Operational overview
├── Audit — Decision detail
├── Audit — Export flow
├── Policy — Active summary + version list
└── Settings — Fail-mode + keys (read-focused v1)

P2 — Hardening & team scale
├── Policy — Validate + activate with diff
├── Inbox — Resolved / expired views
├── Settings — Notification channels
└── Integrations — Runtime status

P3 — Compliance & enterprise adjacency
├── Policy — Visual rule builder
├── Settings — Approver RBAC
├── Audit — Compliance report templates
└── SSO / team management
```

### 5.2 Screen hierarchy tree

```
Level 0 — App shell
└── Level 1 — Primary nav destinations
    ├── Home
    │   └── [widgets only, no L2]
    │
    ├── Inbox
    │   ├── L2: Pending (default)
    │   ├── L2: Resolved
    │   └── L3: Approval detail (/inbox/:approval_id)
    │       └── Modal: Reject reason
    │
    ├── Audit
    │   ├── L2: Timeline (default, filtered)
    │   ├── L3: Decision detail (/audit/:decision_id)
    │   └── L2: Export wizard (/audit/export)
    │
    ├── Policy
    │   ├── L2: Active policy
    │   ├── L2: Version history
    │   ├── L3: Version detail (/policy/:version)
    │   └── L2: Validate (upload/paste)
    │
    └── Settings
        ├── L2: API keys
        ├── L2: Fail-mode
        ├── L2: Notifications
        └── L2: Retention
```

### 5.3 Approval detail — content hierarchy (most important screen)

The approval detail screen is the **decision cockpit**. Content priority top-to-bottom:

1. **Action headline** — `DESTRUCTIVE · delete_record` with outcome urgency styling
2. **One-line decision question** — "Allow subagent_C to delete record T-123 on behalf of user U?"
3. **Primary actions** — Approve · Reject (sticky on mobile — UX-07)
4. **Risk & policy** — tier, matched rule, policy version
5. **Delegation chain** — visual hop diagram, not JSON (UX-05)
6. **Arguments** — redacted, collapsible, sanitized
7. **Session context** — link to N prior decisions in this session
8. **Metadata** — runtime, agent_id, timestamps, TTL remaining

**Anti-pattern:** Table row with "Approve" button and no detail page — insufficient for DESTRUCTIVE/CRITICAL decisions.

### 5.4 Audit timeline — content hierarchy

1. **Time range selector** (default: 24h — UX-09)
2. **Filter bar** — session, agent, runtime, outcome, risk tier, policy version
3. **Grouped rows** — by session (collapsible) or flat chronological
4. **Row density** — timestamp · outcome badge · tool · agent · risk · policy v
5. **Decision detail** — full record + approval resolution join

---

## 6. User Workflows

### 6.1 Workflow A — First-time setup (missing from spec)

**Actor:** Arjun  
**Goal:** Govern first NexusFlow tool call  
**Current spec gap:** No onboarding workflow; jumps to Docker + YAML.

**Recommended flow:**

```
1. Deploy (Docker Compose)           → health check passes
2. Console: enter admin API key        → auth gate
3. Home: "No decisions yet"            → CTA: View integration guide
4. Integrations: copy govern endpoint  → wire NexusFlow hook
5. Trigger test tool call              → first decision in Audit
6. Home: confirms pipeline live        → success state
```

**Reference:** Stripe "Activate payments" checklist; Vercel "Deploy your first project."

---

### 6.2 Workflow B — Escalation triage (core HITL loop)

**Actor:** Priya / Arjun  
**Trigger:** Agent receives ESCALATE  
**Frequency:** Highest-value operator workflow

```
Agent runtime                    Operator (Console)
     │                                │
     ├─ POST /govern/tool-use         │
     ├─ ESCALATE returned             │
     ├─ poll loop starts              │
     │                                ├─ [GAP] Notification (email/push/browser)
     │                                ├─ Inbox badge increments
     │                                ├─ Open approval detail
     │                                ├─ Review chain + args + session history
     │                                ├─ Approve OR Reject (+ reason)
     ├─ poll returns APPROVED/REJECTED │
     └─ execute or abort              └─ Item moves to Resolved
```

**Friction points (documented):**

| Step | Issue | ID |
|------|-------|-----|
| Discovery | No notification; must poll UI/CLI | UX-03 |
| Wait | Agent blocked 300s default; ties up workers | UX-01 |
| Approve race | Late approve after agent timeout | DC-06 |
| Concurrent approve | 409 conflict, optimistic UI risk | UX-06 |
| Mobile | On-call cannot act | UX-07 |

**Recommended product behaviors:**

- Inbox sorted by **risk tier DESC, then age ASC** (CRITICAL first)
- Show **TTL countdown** on each pending item
- On approve/reject: **pessimistic confirm** for DESTRUCTIVE+ (not optimistic update)
- 409 response → "Already resolved by [approver] at [time]" + refetch (Linear merge conflict pattern)
- Poll response includes **queue position** for runtime UX (UX-01 mitigation)

---

### 6.3 Workflow C — Incident reconstruction

**Actor:** Priya  
**Trigger:** "What did the agent do in session X?"  
**Frequency:** Post-incident; compliance review

```
1. Audit → filter by session_id
2. View session timeline (all decisions chronologically)
3. Identify ESCALATE/DENY events
4. Click decision → see approval resolution + reason
5. Note policy_version at time of decision
6. [Optional] Export session bundle for record
```

**Gap:** Spec defines API filters but not **session-as-primary-object** UX. Operators think in sessions; the data model supports it; the UI does not.

**Recommendation:** `/audit?session=sess_abc` opens a **session timeline view** — not a flat table. Reference: Intercom conversation view, Stripe payment intent timeline.

---

### 6.4 Workflow D — Policy change without redeploy

**Actor:** Arjun / Priya  
**Trigger:** New rule needed (e.g., DESTRUCTIVE → ESCALATE)

**Current v0 flow:** Edit YAML → restart API  
**Target v1 flow:**

```
1. Policy → Validate
   └── Paste/edit YAML → schema errors inline (UX-10)
2. Policy → Save as draft version (v4)
3. Policy → Preview impact
   └── "0 decisions would change outcome in last 7d" (shadow mode, Phase 4)
4. Policy → Activate v4
   └── Confirmation modal: "Active policy will change. Agents unaffected."
5. Audit → filter policy_version=v4
   └── Verify new decisions reference v4
6. [Rollback] Policy → Activate v3
```

**Reference:** Stripe Dashboard config changes with immediate effect; Vercel env var promotion with confirmation.

**Gap:** No "preview impact" or shadow mode until Phase 4 — high-risk policy edits remain blind.

---

### 6.5 Workflow E — Fail-mode incident

**Actor:** Arjun  
**Trigger:** ASL unreachable  
**Frequency:** Rare; high severity

```
1. Agent runtime applies local fail-mode
2. [GAP] Operator not notified automatically
3. Agent user sees inconsistent behavior (UX-11)
4. Operator notices via Home health widget OR agent error reports
5. Audit gap during outage (DC-07)
6. Post-recovery: degraded decisions backfilled
7. Audit → filter degraded=true → review gap period
```

**Product gap:** No **degraded mode** visibility in Console. Operators discover outages reactively.

**Recommendation:** Home status banner — "ASL unreachable since 10:04 · agents operating in fail-mode · 12 local decisions pending backfill."

---

### 6.6 Workflow F — Compliance export (Rajesh persona)

**Actor:** Rajesh (future)  
**Trigger:** Regulatory inquiry

```
1. Audit → Export
2. Select date range + filters (WRITE/DESTRUCTIVE, human-approved only)
3. Choose format (CSV/JSON)
4. Async job → download
5. Report includes: decision, policy version, approver, timestamp, principal
```

**Gap:** Export deferred; Rajesh persona blocked until Phase 6+. IA should reserve Export as first-class Audit sub-nav, not buried in Settings.

---

### 6.7 Workflow G — Integrator onboarding (Dev persona)

**Actor:** Dev  
**Surface:** Developer Hub (docs), not Console

```
1. Read OpenAPI + curl examples
2. Copy request schema (tool, args, agent_id, session, principal)
3. Implement pre-tool-call hook
4. Configure fail-mode + health poll
5. Test: ALLOW, DENY, ESCALATE paths
6. Test: outage → fail-mode behavior
```

**Product note:** Dev workflow is well-specified at API level. Do not force Dev through Console auth. Docs are the product.

---

## 7. UX Issues

Prioritized product design issues. Severity reflects user impact, not engineering difficulty.

### 7.1 Critical — blocks product viability beyond solo builder

| ID | Issue | User impact | Recommendation |
|----|-------|-------------|----------------|
| **UX-03** | No escalation discovery path | Approvals sit unseen; agents hang until TTL | Ship notification before UI polish: webhook or email minimum; Inbox badge + browser push in Phase 6 |
| **UX-01** | Agent blocked on sync poll during ESCALATE | Multi-agent stacks compound; voice unusable | Document async pattern; show TTL in approval; runtime timeout < approval TTL; queue position in poll response |
| **UX-NEW-01** | No operational Home | Operator lacks situational awareness | Add Home as P1, not P2 — pending count, health, recent denials |
| **UX-NEW-02** | Approval detail underspecified | Cannot make informed DESTRUCTIVE decisions | Approval detail is P0, not an enhancement (UX-05) |
| **UX-NEW-03** | Session not a first-class audit object | Incident reconstruction is table-scrolling | Session timeline view with grouped decisions |

### 7.2 High — friction for team and compliance personas

| ID | Issue | User impact | Recommendation |
|----|-------|-------------|----------------|
| **UX-02** | Voice sync gate latency | OmniFlow CRM actions feel broken in conversation | Pre-approved session scope UX in policy; voice-specific tool tier; measure before building OmniFlow UI |
| **UX-05** | Insufficient approval context | Slow or wrong approvals | Chain visualization, session link, tool description from policy metadata |
| **UX-06** | 409 concurrent approval | False confidence on approve | Pessimistic UI for DESTRUCTIVE; "Resolved by X" state |
| **UX-09** | Audit overwhelm | Cannot reconstruct incidents | Default 24h window; session grouping; saved filters |
| **UX-10** | YAML-only policy editing | Rajesh blocked; Arjun error-prone | Validate UI before visual editor; inline schema errors |
| **UX-NEW-04** | Policy activate without confirmation | Catastrophic misconfiguration | Confirm modal + show diff vs active; rollback one click |
| **UX-NEW-05** | No cross-linking between Inbox ↔ Audit ↔ Policy | Cognitive load, copy-paste IDs | Every entity page links to related objects |

### 7.3 Medium — polish and scale

| ID | Issue | User impact | Recommendation |
|----|-------|-------------|----------------|
| **UX-04** | Raw API key in sessionStorage | Security UX; no logout story | Key fingerprint display; explicit logout; HTTP-only cookie proxy path |
| **UX-07** | No mobile approval | On-call blocked | Responsive approval detail; sticky actions; PWA consider |
| **UX-08** | DENY reason not actionable for agent | Agent can't recover gracefully | Reason code catalog with agent handling guide in Dev Hub |
| **UX-11** | Fail-mode invisible to end user | Confusing agent behavior during outage | Runtime surfaces degraded banner; Console shows fail-mode period |
| **UX-NEW-06** | Admin UI gated behind "script bottleneck" | Priya/Rajesh personas never validated | Gate UI on persona need, not script annoyance — compliance needs export UI early |
| **UX-NEW-07** | No global search / command palette | Slow navigation at scale | ⌘K jump to session/decision/approval |
| **UX-NEW-08** | Integrator and operator surfaces conflated | Wrong features in wrong place | Split Console vs Developer Hub |

### 7.4 Low — acceptable deferrals with documentation

| ID | Issue | Notes |
|----|-------|-------|
| **UX-09** (partial) | Export UX unspecified | Define export wizard before Phase 6 |
| **S-02** | Polling amplification | Product concern: Inbox 5s poll + N agents polling — show "system load" only if needed |

---

## 8. Enterprise SaaS Patterns

### 8.1 Patterns ASL should adopt (proven, right-sized for v1)

| Pattern | Source | ASL application |
|---------|--------|-----------------|
| **Inbox triage** | Linear, Intercom | Inbox as default landing for operators; badge count; sort by urgency |
| **Immutable audit log with filters** | Stripe Events, Vercel Logs | Audit timeline with outcome badges, export, decision detail |
| **Versioned config with rollback** | Vercel deployments, Stripe API versions | Policy versions: activate, rollback, never delete |
| **Scoped API keys** | Stripe restricted keys | Separate govern vs admin keys; shown in Settings |
| **Status / health surface** | Vercel, Stripe status | Home widget + header indicator |
| **Confirm destructive actions** | Stripe, Linear | Approve DESTRUCTIVE/CRITICAL requires explicit confirm |
| **Async export jobs** | Stripe Sigma exports | Audit export with job status + download |
| **Empty states with CTAs** | Intercom, Vercel | "No pending approvals" → link to integration guide |

### 8.2 Patterns to defer (enterprise scope creep)

| Pattern | Why defer |
|---------|-----------|
| Multi-tenant org/workspace switcher | Explicit non-goal v1 |
| SSO / SAML | Phase 5+ gate |
| Custom roles & permissions UI | Single-operator v1; document RBAC model first |
| Real-time collaboration (live cursors) | Unnecessary for approval queue |
| Full observability platform | Metrics in Grafana sufficient; not a product surface |
| Visual workflow builder | Policy is YAML in v1; visual editor Phase 5 |

### 8.3 Patterns ASL should NOT copy blindly

| Pattern | Risk for ASL |
|---------|--------------|
| **Stripe's dashboard breadth** | ASL is narrow-purpose; 3-job console beats 30-page dashboard |
| **Linear's keyboard-first everything** | Approval is occasional; mobile + notifications matter more |
| **Intercom's conversation-centric IA** | Agent sessions ≠ human conversations; don't over-metaphor |
| **Vercel's project/env hierarchy** | No projects in v1; single-tenant. Add workspace only when multi-team |

### 8.4 Enterprise SaaS checklist (v1 readiness)

| Capability | Spec status | Product design status |
|------------|-------------|----------------------|
| Human approval with attribution | ✓ P0 | Approval detail underspecified |
| Queryable audit by session/time | ✓ P0 | Session timeline missing |
| Policy version on every record | ✓ P0 | Policy UI read-only only |
| Export for compliance | P1 deferred | No export workflow designed |
| Scoped credentials | Deferred Phase 6 | Settings IA not defined |
| Fail-mode configuration | ✓ P0 | No operator UI for fail-mode |
| Approver routing by risk tier | P1 | No assignee UX in Inbox |
| Notification on escalation | P2 | Critical gap — should be P1 |
| RBAC for approvers | Unresolved | Blocks Priya persona at scale |
| Tamper-evident audit | P2 | Rajesh persona partial |

---

## 9. Persona × Surface Matrix

| Job | Arjun | Priya | Rajesh | Dev |
|-----|-------|-------|--------|-----|
| Approve escalation | CLI → Inbox | Inbox | Inbox (read-only role) | — |
| Reject with reason | CLI → Inbox | Inbox | — | — |
| Query audit | CLI → Audit | Audit session view | Audit + Export | — |
| Change policy | YAML/CLI → Policy | Policy activate | — | — |
| Integrate runtime | Docs | — | — | Dev Hub |
| Configure fail-mode | Settings/CLI | Settings | — | SDK config |
| Manage API keys | Settings/CLI | Settings | — | — |
| Export compliance report | — | Audit Export | Audit Export | — |

**Design implication:** v1 Console MVP = **Inbox + Audit + Policy (read) + Settings (keys, fail-mode)**. Home and Export unlock Priya/Rajesh.

---

## 10. Recommended Phasing (Product Design)

Aligns with [PLAN.md](./PLAN.md) but adjusts UI priorities by persona need, not script annoyance alone.

### Phase 6 minimum viable Console (if UI gate opens)

1. Auth gate (API key)
2. **Inbox** — pending list + **approval detail** (not list-only)
3. **Audit** — filtered timeline + decision detail
4. **Policy** — active version display
5. Inbox badge + 5s poll (already planned)

### Phase 6 + 30 days (persona completion)

6. **Home** — operational overview
7. **Audit export** wizard
8. **Notification** — webhook or email on new escalation
9. Session timeline view
10. Settings — fail-mode, keys

### Phase 4+ (policy safety)

11. Policy validate + activate with diff/confirm
12. Shadow mode impact preview
13. Resolved/expired Inbox tabs

### Phase 5 (Rajesh)

14. Compliance export templates
15. Read-only operator role
16. Guided onboarding (non-YAML)

---

## 11. Open Product Design Decisions

Resolve before building admin UI:

| # | Decision | Options | Recommendation |
|---|----------|---------|----------------|
| 1 | Default landing page | Home vs Inbox | **Inbox** if pending > 0, else Home |
| 2 | Approval list vs detail-first | Split pane vs routes | **Routes** — `/inbox/:id` for mobile shareability |
| 3 | Audit default view | Flat table vs session groups | **Flat timeline** with "group by session" toggle |
| 4 | Policy editing in UI | Read-only vs validate-only vs full editor | **Validate + activate** in v1; edit in YAML |
| 5 | Auth model | API key in browser vs cookie proxy | **Cookie proxy** before team use (SEC-05) |
| 6 | Notification MVP | Email vs webhook vs browser | **Webhook + browser** for Arjun; email for Rajesh |
| 7 | Reject flow | Modal vs inline | **Modal** with required reason for DESTRUCTIVE+ |
| 8 | Concurrent approvers | First-wins vs assignee lock | **First-wins** with clear 409 UX (already architectural) |

---

## 12. Summary Scorecard

| Area | Grade | One-line assessment |
|------|-------|---------------------|
| API / integrator UX | A- | Clear contract; Dev persona well served by docs |
| Operator IA | D+ | Three pages listed; no hierarchy, linking, or home |
| HITL / Inbox UX | C- | Core loop exists in API; discovery and detail view weak |
| Audit / investigation UX | C | Filters in API; session timeline and export missing |
| Policy lifecycle UX | D | YAML-first acceptable for Arjun; no safe activate/rollback UX |
| Enterprise patterns | Incomplete | Right instincts (versioned policy, scoped keys); UI not designed |
| Persona alignment | Misaligned | Four personas; one undifferentiated deferred UI |
| Onboarding | Missing | No time-to-first-value workflow |

**Bottom line:** ASL's backend product is ahead of its operator product. Before Phase 6 UI work, define the Console IA, approval detail spec, session timeline, and notification path. The admin UI is not three tables — it is an **inbox-first control plane** with audit investigation and policy lifecycle as peer workflows. Ship like Linear triages issues, not like a CRUD scaffold.

---

*Audit completed pre-build. Revisit when Phase 6 gate opens or personas change.*
