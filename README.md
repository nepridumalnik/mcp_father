# MCP Father Hub

An MCP (Model Context Protocol) hub that allows you to manage multiple MCP servers as plugins.

## Features

- **Plugin Management**: Register, enable, disable, and sync MCP plugins from Git repositories.
- **Centralized Configuration**: Manage all plugins through `repositories/list.yml` and `~/.mcp_father/settings.json`.
- **Built-in Tools**: Includes utility tools like timestamp, hostname, and directory creation.
- **Dynamic Mounting**: Plugins are automatically mounted as part of the hub.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/mcp_father.git
   cd mcp_father
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Before using the hub commands, initialize the local configuration:

```bash
python -m mcp_father init
```

### Initialization

Initialize the configuration files:
```bash
python -m mcp_father init
```

### Managing Plugins

- **List plugins**:
  ```bash
  python -m mcp_father list
  ```

- **Enable a plugin**:
  ```bash
  python -m mcp_father enable example-plugin
  ```

- **Disable a plugin**:
  ```bash
  python -m mcp_father disable example-plugin
  ```

- **Sync plugins** (clones/updates repos):
  ```bash
  python -m mcp_father sync
  # or for a specific plugin
  python -m mcp_father sync example-plugin
  ```

- **Lock to a commit**:
  ```bash
  python -m mcp_father lock example-plugin <commit-hash>
  ```

### Running the Hub

Start the MCP server:
```bash
python -m mcp_father run
```

### Debug Logging

Enable DEBUG logging with `-d` or `--debug` before or after the command:
```bash
python -m mcp_father -d run
python -m mcp_father run -d
```

## Example Configuration

**repositories/list.yml**
```yaml
repositories:
  example-plugin:
    url: "https://github.com/example/example-mcp.git"
    branch: "main"
    namespace: "example"
    mcp:
      command: "uv"
      args: ["run", "python", "-m", "example_mcp"]
```

**~/.mcp_father/settings.json**
```json
{
  "plugins": {
    "example-plugin": {
      "enabled": true,
      "locked_commit": null
    }
  }
}
```

## Connecting to Claude/Qwen
Configure your MCP client (e.ry Claude Desktop) to use the hub:
```json
{
  "mcpServers": {
    "mcp-father": {
      "command": "python",
      "args": ["/path/to/mcp_father/__main__.py"]
    }
  }
}
```
