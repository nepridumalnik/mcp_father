from .utils import get_timestamp, get_hostname, create_directory

from fastmcp import FastMCP


def mount_tools(mcp: FastMCP) -> None:
    """
    Registers system utility functions as MCP tools.

    Args:
        mcp (FastMCP): The FastMCP instance to which tools will be attached.
    """

    # Utils
    mcp.tool()(get_timestamp)
    mcp.tool()(get_hostname)
    mcp.tool()(create_directory)


def start() -> None:
    mcp = FastMCP("mcp_hub")

    mount_tools(mcp)

    mcp.run()
