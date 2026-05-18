from fastmcp import FastMCP
from .utils.system import get_timestamp, get_hostname, create_directory

def register_builtin_tools(mcp: FastMCP):
    """Registers the built-in utility tools to the FastMCP instance."""
    
    @mcp.tool()
    def get_timestamp_tool() -> str:
        """Returns the current system timestamp."""
        return get_timestamp()

    @mcp.tool()
    def get_hostname_tool() -> str:
        """Returns the hostname of the machine."""
        return get_hostname()

    @mcp.tool()
    def create_directory_tool(path: str) -> str:
        """Creates a new directory at the specified path."""
        return create_directory(path)

