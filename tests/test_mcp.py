"""MCP server tests, the MCP bonus surface (``mcp_server``).

These tests use the in-memory transport: the server object is wired straight to a client
session, with no subprocess and no network. The coroutines are driven with ``asyncio.run``
so no async test plugin is needed, and no LLM or API key is involved. The DB-backed
round-trip uses the shared ``db`` fixture.
"""

from __future__ import annotations

import asyncio
import json

import pytest
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp.shared.memory import create_connected_server_and_client_session as connect

from mcp_server.server import build_server
from tools.metrics import get_otb_summary

REQUIRED_TOOL_NAMES = {
    "get_otb_summary",
    "get_segment_mix",
    "get_pickup_delta",
    "get_as_of_otb",
    "get_block_vs_transient_mix",
}


async def _load_tools_over_mcp() -> list:
    """Connect a client to the server over the in-memory transport and load its tools."""
    server = build_server()
    async with connect(server) as session:
        return await load_mcp_tools(session)


async def _call_over_mcp(tool_name: str, args: dict):
    """Invoke a single MCP tool over the in-memory transport and return its result."""
    server = build_server()
    async with connect(server) as session:
        tools = {t.name: t for t in await load_mcp_tools(session)}
        return await tools[tool_name].ainvoke(args)


def _as_dict(result):
    """Normalise an MCP tool result to a dict.

    Over MCP a tool returns content blocks (``[{"type": "text", "text": "<json>"}]``);
    the adapter may also hand back a plain JSON string or an already-parsed dict.
    """
    if isinstance(result, dict):
        return result
    if isinstance(result, list):
        result = "".join(
            block.get("text", "")
            for block in result
            if isinstance(block, dict) and block.get("type") == "text"
        )
    return json.loads(result)


def test_mcp_exposes_exactly_the_five_tools():
    """Over MCP, the catalog is exactly the five named tools, no SQL tool, all documented."""
    tools = asyncio.run(_load_tools_over_mcp())
    names = {t.name for t in tools}
    assert names == REQUIRED_TOOL_NAMES
    assert not any("sql" in name.lower() for name in names)
    # Each tool carries a description.
    assert all((t.description or "").strip() for t in tools)


@pytest.mark.db
def test_mcp_round_trip_matches_direct(db):
    """A tool called over MCP returns the same result as the in-process tool (not a stub)."""
    over_mcp = _as_dict(asyncio.run(_call_over_mcp("get_otb_summary", {"stay_month": "2025-07"})))
    direct = get_otb_summary.invoke({"stay_month": "2025-07"})
    # Normalise both through JSON so numeric types line up (the MCP result crossed JSON).
    assert over_mcp == json.loads(json.dumps(direct))
