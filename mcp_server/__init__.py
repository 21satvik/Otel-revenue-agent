"""MCP server package: publishes ``tools.metrics.ALL_TOOLS`` over the Model Context Protocol."""

from mcp_server.server import SERVER_NAME, build_server

__all__ = ["SERVER_NAME", "build_server"]
