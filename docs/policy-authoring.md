# Policy authoring guide

How to write, evaluate, and deploy ASL policy documents.

## Document structure

Policies are YAML files validated against `packages/asl-schemas/jsonschema/policy-v1.json`.
See `policies/examples/default-policy.yaml` for a working baseline.

Required top-level fields:

| Field | Description |
|-------|-------------|
| `schema_version` | Policy schema version (`"1.0"` in v0) |
| `version` | Immutable policy version id (`v1`, `v2`, …) |
| `default_unclassified` | Decision when a tool has no classification entry |
| `rules` | Ordered list of rules evaluated at govern time |

## ADR: Rule precedence (TD-02)

**Status:** Accepted (Phase 0)  
**Context:** Multiple rules may match a single govern request. Without explicit precedence, operators cannot predict outcomes.

**Decision:** **First-match-wins, top-to-bottom.**

1. Classify the tool into a risk tier (`READ`, `WRITE`, `DESTRUCTIVE`, `CRITICAL`) using `tool_classifications`.
2. If the tool is absent from `tool_classifications`, apply `default_unclassified` and **do not** evaluate `rules`.
3. Otherwise, iterate `rules` in array order. The **first** rule whose `when` conditions match wins.
4. If no rule matches, apply `default_unclassified`.

**Consequences:**

- Place more specific rules **above** broader catch-all rules.
- Reordering rules changes behavior — treat order as significant in code review.
- Composite conditions (e.g. `session_rejection_count_gte`) are evaluated only when a rule is reached in order.

**Alternatives rejected:**

- *Highest priority number* — adds authoring burden; YAML order is visible in diffs.
- *Most-specific wins* — ambiguous for overlapping tier lists; harder to test.

## Unclassified tools (SEC-01)

`default_unclassified` controls tools not listed in `tool_classifications`:

| Value | Behavior |
|-------|----------|
| `ESCALATE` | **Recommended default** — human reviews unknown tools |
| `DENY` | Strictest; blocks until classification is added |
| `ALLOW` | **Avoid in production** — bypasses governance for unknown tools |

The example policy ships with `default_unclassified: ESCALATE`.

## Reason code catalog

Machine-readable codes returned in govern responses and stored on `decision_records.reason_code`:

| Code | When |
|------|------|
| `POLICY_ALLOW` | A rule matched with `then: ALLOW` |
| `POLICY_DENY` | A rule matched with `then: DENY` |
| `POLICY_ESCALATE` | A rule matched with `then: ESCALATE` |
| `UNCLASSIFIED_ESCALATE` | Unclassified tool; `default_unclassified` is `ESCALATE` |
| `UNCLASSIFIED_DENY` | Unclassified tool; `default_unclassified` is `DENY` |
| `APPROVAL_APPROVED` | Poll status after human approval (Phase 1+) |
| `APPROVAL_REJECTED` | Poll status after human rejection |
| `APPROVAL_EXPIRED` | Approval TTL elapsed before resolution |

## v0 deployment model

Phase 0–2 load a single policy file at API startup. Versioned deploy/rollback APIs are deferred.
Store policies in git; change the mounted file and restart the API to update rules.

## Authoring checklist

- [ ] Every production tool appears in `tool_classifications`
- [ ] `default_unclassified` is `ESCALATE` or `DENY`
- [ ] Rules are ordered most-specific first
- [ ] DESTRUCTIVE and CRITICAL tiers escalate or deny
- [ ] Run `validate` (Phase 1 CLI) before activating a new version
