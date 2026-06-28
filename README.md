# Agentic Safety Layer (ASL)

External governance control plane for agent tool calls — policy evaluation, human escalation, and durable audit.

**Status:** Phase 0 (foundation) complete. Policy engine and NexusFlow integration ship in Phases 1–2.

## Quickstart

### Prerequisites

- Docker and Docker Compose
- Python 3.12+ (for local development without Docker)

### Run with Docker

```bash
cp .env.example .env
# Edit ASL_API_KEY in .env before any non-local use

docker compose up --build
```

Services:

| Service | URL |
|---------|-----|
| API | http://localhost:8000 |
| Health | http://localhost:8000/api/v1/health |
| OpenAPI docs | http://localhost:8000/api/v1/docs |

Migrations run automatically on API startup.

### Authenticate a govern call

```bash
curl -s -X POST http://localhost:8000/api/v1/govern/tool-use \
  -H "Authorization: Bearer ${ASL_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "schema_version": "1.0",
    "tool": "update_ticket",
    "arguments": {"ticket_id": "T-123"},
    "agent_id": "nexusflow/support-agent",
    "session_id": "sess_demo",
    "timestamp": "2026-06-28T10:00:00Z",
    "principal": {"type": "user", "id": "user:U42"}
  }'
```

Phase 0 returns a stub `ALLOW` response. Real policy evaluation arrives in Phase 1.

### Local development (API only)

```bash
cd apps/api
pip install -e ".[dev]"

# Start Postgres (or use docker compose up postgres -d)
export DATABASE_URL=postgresql+asyncpg://asl:asl_dev_password@localhost:5432/asl
export DATABASE_URL_SYNC=postgresql+psycopg://asl:asl_dev_password@localhost:5432/asl
export ASL_API_KEY=asl_dev_change_me

alembic upgrade head
uvicorn asl.main:app --reload
```

### Database bootstrap

After migrations, apply least-privilege roles (TD-12):

```bash
chmod +x deploy/scripts/init-db.sh
./deploy/scripts/init-db.sh
```

### Tests and lint

```bash
cd apps/api
pip install -e ".[dev]"
alembic upgrade head   # requires Postgres
pytest ../../tests -v
ruff check src ../../tests
mypy src
lint-imports
```

## Repository layout

```
apps/api/           FastAPI backend (deployable)
packages/asl-schemas/   OpenAPI + JSON Schema contracts
policies/           Example policy artifacts
deploy/             Init scripts, future nginx/grafana
integrations/       NexusFlow/OmniFlow hooks (Phase 2+)
tests/              Integration and contract tests
docs/               Policy authoring guide
```

Deferred to later phases: `apps/cli`, `apps/admin-ui`, `packages/asl-client`.

## Non-goals (v0)

These are explicitly **out of scope** until after the Phase 2 finish line:

- Admin UI, CLI package, Python SDK
- Policy deploy/rollback HTTP API
- Multi-key management, rotation, scoped keys (v0 uses single `ASL_API_KEY`)
- OmniFlow integration
- Composite session-context rules in the policy engine
- Webhooks, SSO, multi-tenant SaaS, HA clustering
- Enterprise control-plane feature parity (Galileo ACP, Kore.ai AMP)

See [PROJECT_BRIEF.md](./PROJECT_BRIEF.md) and [PLAN.md](./PLAN.md) for the full roadmap.

## Documentation

- [ARCHITECTURE.md](./ARCHITECTURE.md) — system design
- [PLAN.md](./PLAN.md) — implementation phases
- [docs/policy-authoring.md](./docs/policy-authoring.md) — rule precedence ADR
- [packages/asl-schemas/openapi/asl-v1.yaml](./packages/asl-schemas/openapi/asl-v1.yaml) — API contract
