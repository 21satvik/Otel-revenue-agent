# Revenue Manager Agent

An AI **Revenue Manager** for a hotel General Manager. Ask it commercial questions
about the reservation book in plain English ("how is August shaping up?", "are we
too dependent on OTAs?", "what changed in the last 7 days?") and it answers like a
morning commercial briefing: headline, drivers, the risk or opportunity, and a
recommended action, with the numbers that matter and nothing that doesn't.

It is built as a **LangChain Deep Agent** over a Postgres reservation book. The
numbers never come from the model improvising SQL; they come from five typed,
tested tools that read semantic views, so grain, default filters, and date logic
are correct by construction.

```
ETL (Playwright scrape -> typed transform -> idempotent load)
  -> Postgres -> semantic views -> 5 typed tools
  -> Deep Agent (skills - segment subagent - HITL approval - memory)
  -> FastAPI gateway (basic-auth chat - SSE tool/skill streaming) + chat UI
        |
        +-- the same 5 tools are also published as an MCP server
```

## What's interesting here

- **Correctness lives in code, not the prompt.** Hotel revenue data has sharp edges:
  the fact table is one row per reservation x stay-date, so a reservation count is
  `count(distinct reservation_id)` and room nights are `sum(number_of_spaces)`, never
  a row count. Cancelled and provisional business is excluded by default. Pickup is
  measured on booking time (a trailing window), monthly figures on stay date, and
  market macro groups are stay-date-effective (they change over time). All of that is
  enforced in the tool layer and the semantic views, and covered by tests.
- **No `run_sql` tool.** The agent composes answers only from the five named tools,
  which read views, never raw tables. The model cannot reach the database directly.
- **The full Deep Agents surface, each piece chosen deliberately:** skills (progressive
  disclosure), a quarantined segment-mix subagent, a human-in-the-loop approval gate on
  the expensive point-in-time rebuild, and checkpointer + store for multi-turn memory.
- **Provider-agnostic model.** `MODEL_ID` selects the chat model via LangChain's
  `init_chat_model` (Claude by default; Groq, OpenAI, etc. work by changing one env var).
- **MCP server.** The same five tools are published as a standalone Model Context
  Protocol server, so any MCP client can reuse them, with a single source of truth.
- **Streaming UI.** A small chat page renders each tool call and skill load live over
  Server-Sent Events, expandable to inputs, results, and latency.

## Quickstart (self-contained demo)

No scrape and no external data source required. You need
[uv](https://docs.astral.sh/uv/), Docker (for local Postgres), and a model API key.

```bash
uv sync --extra dev

# 1. Local Postgres (the schema is mounted at init)
docker compose up -d
export DATABASE_URL=postgresql://revenue:revenue@localhost:5432/hotel_revenue

# 2. Seed a deterministic demo dataset (applies the FK override + semantic views, loads data)
uv run python -m scripts.seed_demo

# 3. Serve the agent (set your model key, e.g. ANTHROPIC_API_KEY, and BASIC_AUTH_*)
uv run uvicorn app.server:app --host 0.0.0.0 --port 8000
# open http://localhost:8000  (basic auth: BASIC_AUTH_USER / BASIC_AUTH_PASS)
```

The demo dataset is hand-built to exercise every scenario the agent reasons about
(multi-night and multi-room stays, cancellations, provisional business, OTA
concentration, an effective-vs-static macro-group reclassification, group/block vs
transient, and point-in-time differences). Its stay dates sit in 2025, so ask about
those months explicitly, for example "the on-the-books summary for August 2025" or
"which segments are driving September 2025?". The agent resolves a bare "this month"
against the real current date and will correctly report other months as outside the
loaded window.

## Layout
| Path | What |
|------|------|
| `etl/` | `scrape.py` (Playwright) - `transform.py` (typed, grain) - `load.py` (idempotent) - `run_etl.py` |
| `sql/views.sql` | semantic views (`vw_stay_night_base`, `vw_segment_stay_night`, `vw_stay_night_posted`) |
| `tools/` | `metrics.py` (the 5 tools) - `db.py` (read-only access) - `METRIC_DEFINITIONS.md` |
| `skills/` | 8 `SKILL.md` skills + `SKILL_INDEX.md` (the pack index) |
| `agent/` | `build.py` (`create_deep_agent` wiring) - `subagents.py` - `prompt.py` |
| `mcp_server/` | publishes the 5 tools over MCP; the agent can consume them over the protocol |
| `app/` | `server.py` (FastAPI) - `static/index.html` (chat UI) |
| `scripts/` | `seed_demo.py` (demo data) - `apply_views.py` |
| `tests/` | `test_etl.py` - `test_tools.py` - `test_skills.py` - `test_agent.py` - `test_mcp.py` + synthetic fixture |

## The five tools
| Tool | Answers |
|------|---------|
| `get_otb_summary` | on-the-books revenue, room nights, ADR, occupancy, RevPAR for a stay month |
| `get_segment_mix` | segment/channel mix and shares, with the effective macro group |
| `get_pickup_delta` | what was booked in a trailing window (pace), with per-segment shares |
| `get_as_of_otb` | point-in-time on-the-books as of a past instant (gated by human approval) |
| `get_block_vs_transient_mix` | group/block vs transient split and top-account concentration |

## Tests
`uv run pytest` runs every suite against an isolated `*_test` database (derived from
`DATABASE_URL` and auto-created, or set `TEST_DATABASE_URL`), so it never disturbs a
working load:
- `test_etl.py` / `test_tools.py` run against the database, loading the deterministic
  synthetic fixture (`tests/fixture_data.py`), so they pass with no scrape.
- `test_skills.py` / `test_agent.py` are structural / graph-introspection with a fake
  injected model. No LLM API calls.
- `test_mcp.py` loads the tools over an in-memory MCP transport and checks a tool
  round-trips to the same result as the in-process call. No network or API calls.

CI (`.github/workflows/ci.yml`) spins up Postgres, applies the schema and views, then
runs ruff and the suite.

## MCP server
The same five tools are also published as a standalone **MCP server**, generated from
`tools.metrics.ALL_TOOLS`, so grain, filters, and the read-only guardrail are inherited
and no SQL is exposed. The agent uses in-process tools by default; set
`RM_TOOL_TRANSPORT=mcp` (and `MCP_SERVER_URL=...` for the HTTP server) to consume them
over the protocol instead, in which case only the MCP server holds `DATABASE_URL`.

```bash
uv run python -m mcp_server --transport stdio              # local clients
uv run python -m mcp_server --transport streamable-http    # network service on 127.0.0.1:9000/mcp
```

## Production data pipeline (optional)
The demo seed above is all you need to run the project. In a real deployment the same
Postgres tables are populated by the ETL in `etl/`: a Playwright scrape of the source
reservation system, a pure typed transform that enforces the one-row-per-stay-night
grain, and an idempotent truncate-and-reload that writes a provenance manifest.

```bash
uv run playwright install chromium
uv run python scripts/apply_views.py   # FK override + semantic views
uv run python -m etl.run_etl           # scrape + load + manifest
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full design and the skill-to-tool
routing matrix.
