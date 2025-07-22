# Genymotion SaaS MCP Server

MCP Server for the Genymotion SaaS to interact with the Genymotion SaaS platform to create and manage Android instances

### Features

- List all available Android recipes.
- Start/Stop a new Android instance from a selected recipe.
- Connect or disconnect ADB to a running Android instance.
- Display detailed information about a specific Android recipe.
- List all available Android OS versions for creating new instances.
- Show all currently running Android instances in Genymotion SaaS.

## Setup

### Environment Setup
- Python 3.12.6 required (you can use [pyenv](https://github.com/pyenv/pyenv)).
- Use [uv](https://docs.astral.sh/uv/getting-started/installation/) for dependency management.

#### Install uv
> Please read the official documentation for uv for more options.
```bash

# On macOS and Linux.
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows.
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

Or, from PyPI:

# With pip.
pip install uv

# Or pipx.
pipx install uv
```

### Genymotion SaaS API Token
[Create a Genymotion SaaS API Token](https://docs.genymotion.com/saas/10_Public_HTTP_API/):
   - Go to your [Genymotion SaaS account](https://cloud.geny.io).
   - Navigate to the "API" section.
   - Create and copy the generated token.

### Use with [Claude Desktop](https://claude.ai/download)

Open Claude settings, then navigate to the Developer tab.

Click _Edit config_. This creates a config file called `claude_desktop_config.json`. Open this file with your preferred editor and add the Genymotion MCP server:

```json
{
  "mcpServers": {
    "genymotion": {
      "command": "uvx",
      "env": {
        "GENYMOTION_API_TOKEN": "<YOUR_API_TOKEN>"
      },
      "args": [
        "--from",
        "git+https://github.com/thomascarpentier/genymotion-mcp@v0.0.1",
        "genymotion-mcp"
      ]
    }
  }
}
```

Save the config file and restart Claude Desktop. 

### Use with [Gemini cli](https://github.com/google-gemini/gemini-cli)

Open the file located at `~/.gemini/settings.json`

And add the MCP configuration:

```json
{
  "mcpServers": {
    "genymotion": {
      "command": "uvx",
      "env": {
        "GENYMOTION_API_TOKEN": "<YOUR_API_TOKEN>"
      },
      "args": [
        "--from",
        "git+https://github.com/thomascarpentier/genymotion-mcp@v0.0.1",
        "genymotion-mcp"
      ]
    }
  }
}
```