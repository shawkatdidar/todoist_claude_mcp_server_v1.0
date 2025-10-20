# Todoist MCP Server

MCP server to connect Todoist with Claude through REST API. Manage your Todoist tasks, projects, sections, labels, and comments directly from Claude.

## Features

- **Task Management**: Create, update, complete, and delete tasks
- **Project Management**: View all your Todoist projects
- **Section Management**: Get sections within projects
- **Label Management**: View and use labels for task organization
- **Comments**: Read comments on tasks and projects
- **Advanced Filtering**: Filter tasks by project or label
- **Priority Support**: Set task priorities from 1 (normal) to 4 (urgent)
- **Due Dates**: Set and update task due dates

## Installation

### Via Smithery (Recommended)

```bash
npx @smithery/cli install todoist-mcp-server
```

**During installation, you will be prompted to enter your Todoist API token.**

#### How to get your Todoist API token:
1. Go to [Todoist Settings → Integrations](https://todoist.com/prefs/integrations)
2. Scroll down to the "Developer" section
3. Copy your API token
4. Paste it when Smithery prompts you during installation

### Manual Installation

1. Clone this repository:
```bash
git clone https://github.com/shawkatdidar/todoist_claude_mcp_server_v1.0.git
cd todoist_claude_mcp_server_v1.0
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Get your Todoist API token from [Todoist Settings > Integrations > Developer](https://todoist.com/prefs/integrations)

4. Set up your environment variable:
```bash
export TODOIST_API_TOKEN=your_token_here
```

## Configuration

### For Claude Desktop

Add this to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "todoist": {
      "command": "python",
      "args": ["/path/to/todoist_claude_mcp_server_v1.0/server.py"],
      "env": {
        "TODOIST_API_TOKEN": "your_token_here"
      }
    }
  }
}
```

### For Smithery (Claude.ai)

When installing via Smithery, you'll be prompted to enter your TODOIST_API_TOKEN during setup. Smithery will securely store your token and provide it to the MCP server automatically.

**Note**: Each user needs their own Todoist API token. The token is personal and should not be shared.

## Available Tools

| Tool | Description |
|------|-------------|
| `get_tasks` | Get all tasks with optional filtering by project or label |
| `get_projects` | Get all projects from Todoist |
| `get_sections` | Get all sections, optionally filtered by project |
| `get_labels` | Get all labels from Todoist |
| `get_comments` | Get comments for a specific task or project |
| `create_task` | Create a new task with optional project, section, due date, priority, and labels |
| `update_task` | Update an existing task |
| `complete_task` | Mark a task as complete |
| `delete_task` | Delete a task |

## Usage Examples

Once installed, you can ask Claude:

- "What are my tasks for today?"
- "Create a task to buy groceries with priority 3"
- "Show me all my projects"
- "Complete task [task_id]"
- "Update task [task_id] to have due date 2025-12-31"

## Requirements

- Python 3.10+
- httpx >= 0.27.0
- python-dotenv >= 1.0.0
- mcp >= 0.1.0
- tenacity >= 8.2.0

## License

MIT

## Author

shawkatdidar
