"""MCP server exposing the Revenue-Manager tool layer.

The five read-only tools in ``tools.metrics.ALL_TOOLS`` are published over the Model
Context Protocol so MCP clients can call them and the agent can consume them
out-of-process. In an MCP deployment only this server reads ``DATABASE_URL``; the agent
receives results over the protocol.

The MCP tools are generated from ``ALL_TOOLS`` via ``to_fastmcp``, so each metric has a
single definition in ``tools/metrics.py``. Grain, default filters, and the read-only
transaction guardrail in ``tools/db.py`` are inherited unchanged. No tool accepts a raw
SQL string.
"""

from __future__ import annotations

import argparse
import os

from langchain_mcp_adapters.tools import to_fastmcp
from mcp.server.fastmcp import FastMCP

from tools import MCP_SERVER_NAME
from tools.metrics import ALL_TOOLS

# Canonical service name, shared with the agent's MCP client via the tools core.
SERVER_NAME = MCP_SERVER_NAME


def build_server() -> FastMCP:
    """Build the FastMCP server from ``ALL_TOOLS``.

    Host and port apply only to the network transports (``streamable-http`` / ``sse``)
    and are read from the environment; the default ``stdio`` transport ignores them.
    """
    fastmcp_tools = [to_fastmcp(tool) for tool in ALL_TOOLS]
    return FastMCP(
        SERVER_NAME,
        instructions=(
            "Read-only revenue-management metrics for a hotel. Each tool documents its "
            "grain (stay row, reservation, room night); none accepts raw SQL."
        ),
        tools=fastmcp_tools,
        host=os.environ.get("MCP_HOST", "127.0.0.1"),
        port=int(os.environ.get("MCP_PORT", "9000")),
    )


def main() -> None:
    """Run the server on the chosen transport.

    ``stdio`` serves local clients; ``streamable-http`` serves the network.
    """
    parser = argparse.ArgumentParser(description="Otel Revenue-Manager MCP server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http", "sse"],
        default=os.environ.get("MCP_TRANSPORT", "stdio"),
        help="MCP transport (default: stdio, for local clients like Claude Desktop)",
    )
    args = parser.parse_args()
    build_server().run(transport=args.transport)


if __name__ == "__main__":
    main()
