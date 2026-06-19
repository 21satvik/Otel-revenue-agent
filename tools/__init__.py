"""Shared tool-layer package.

Holds the canonical MCP service name so both the server (which declares it) and the
agent's MCP client (which connects to it) depend on the core, not on each other.
"""

MCP_SERVER_NAME = "revenue-manager-rm"
