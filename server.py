import os
import asyncio
import httpx
from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Load environment variables
load_dotenv()
TODOIST_API_TOKEN = os.getenv("TODOIST_API_TOKEN")

import sys
print("Current working directory:", os.getcwd(), file=sys.stderr, flush=True)
print(".env exists:", os.path.exists(".env"), file=sys.stderr, flush=True)

# Validate API token presence
if TODOIST_API_TOKEN:
    print("TODOIST_API_TOKEN loaded: ****" + TODOIST_API_TOKEN[-4:], file=sys.stderr, flush=True)
else:
    print("ERROR: TODOIST_API_TOKEN not found!", file=sys.stderr, flush=True)
    print("Please set your Todoist API token as an environment variable.", file=sys.stderr, flush=True)
    print("Get your token from: https://todoist.com/prefs/integrations", file=sys.stderr, flush=True)

# Create MCP server
server = Server("todoist-server")

# Global HTTP client for connection pooling
api_client = None

async def get_api_client() -> httpx.AsyncClient:
    """Get or create the API client with connection pooling"""
    global api_client
    if api_client is None:
        api_client = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
    return api_client

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException))
)
async def api_request(method: str, url: str, headers: dict, **kwargs):
    """Make an API request with retry logic"""
    client = await get_api_client()
    response = await client.request(method, url, headers=headers, **kwargs)
    response.raise_for_status()
    return response

def validate_priority(priority: int) -> bool:
    """Validate priority is between 1-4"""
    return 1 <= priority <= 4

def validate_task_id(task_id: str) -> bool:
    """Validate task_id is not empty"""
    return bool(task_id and task_id.strip())

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="get_tasks",
            description="Get all tasks from Todoist",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Filter tasks by project ID (optional)"
                    },
                    "label": {
                        "type": "string",
                        "description": "Filter tasks by label name (optional)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_projects",
            description="Get all projects from Todoist",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_sections",
            description="Get all sections from Todoist, optionally filtered by project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Filter sections by project ID (optional)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_labels",
            description="Get all labels from Todoist",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_comments",
            description="Get comments for a specific task or project",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Task ID to get comments for (optional)"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "Project ID to get comments for (optional)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="create_task",
            description="Create a new task in Todoist",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The task content/description"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "Project ID (optional)"
                    },
                    "section_id": {
                        "type": "string",
                        "description": "Section ID (optional)"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "Due date in YYYY-MM-DD format (optional)"
                    },
                    "priority": {
                        "type": "integer",
                        "description": "Priority from 1 (normal) to 4 (urgent). Default is 1."
                    },
                    "labels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of label names (optional)"
                    }
                },
                "required": ["content"]
            }
        ),
        Tool(
            name="update_task",
            description="Update an existing task in Todoist",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The ID of the task to update"
                    },
                    "content": {
                        "type": "string",
                        "description": "New task content (optional)"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "New due date in YYYY-MM-DD format (optional)"
                    },
                    "priority": {
                        "type": "integer",
                        "description": "New priority from 1-4 (optional)"
                    }
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="complete_task",
            description="Mark a task as complete in Todoist",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The ID of the task to complete"
                    }
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="delete_task",
            description="Delete a task from Todoist",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The ID of the task to delete"
                    }
                },
                "required": ["task_id"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""
    # Check if API token is available
    if not TODOIST_API_TOKEN:
        return [TextContent(
            type="text",
            text="❌ ERROR: TODOIST_API_TOKEN not configured.\n\n"
                 "Please set your Todoist API token:\n"
                 "1. Go to https://todoist.com/prefs/integrations\n"
                 "2. Find 'Developer' section\n"
                 "3. Copy your API token\n"
                 "4. Configure it in your MCP settings"
        )]

    headers = {"Authorization": f"Bearer {TODOIST_API_TOKEN}"}

    try:
        if name == "get_tasks":
            # Build query parameters
            params = {}
            if "project_id" in arguments:
                params["project_id"] = arguments["project_id"]
            if "label" in arguments:
                params["label"] = arguments["label"]

            response = await api_request(
                "GET",
                "https://api.todoist.com/rest/v2/tasks",
                headers=headers,
                params=params
            )

            tasks_raw = response.json()
            tasks_clean = []
            for task in tasks_raw:
                tasks_clean.append({
                    "id": task["id"],
                    "content": task["content"],
                    "project_id": task.get("project_id"),
                    "section_id": task.get("section_id"),
                    "due": task["due"]["date"] if task.get("due") else None,
                    "priority": task["priority"],
                    "labels": task.get("labels", []),
                    "url": task.get("url")
                })

            result = f"Found {len(tasks_clean)} tasks:\n\n"
            for task in tasks_clean:
                result += f"• {task['content']}"
                if task['due']:
                    result += f" (Due: {task['due']})"
                result += f" [Priority: {task['priority']}]"
                if task['labels']:
                    result += f" Labels: {', '.join(task['labels'])}"
                result += f"\n  ID: {task['id']}, Project: {task['project_id']}\n"

            return [TextContent(type="text", text=result)]
    
        elif name == "get_projects":
            response = await api_request(
                "GET",
                "https://api.todoist.com/rest/v2/projects",
                headers=headers
            )

            projects = response.json()
            result = f"Found {len(projects)} projects:\n\n"
            for project in projects:
                result += f"• {project['name']}\n"
                result += f"  ID: {project['id']}"
                if project.get('parent_id'):
                    result += f", Parent ID: {project['parent_id']}"
                result += f", Color: {project.get('color', 'N/A')}"
                result += f", Favorite: {project.get('is_favorite', False)}"
                if project.get('view_style'):
                    result += f", View: {project['view_style']}"
                result += "\n\n"

            return [TextContent(type="text", text=result)]
    
        elif name == "get_sections":
            params = {}
            if "project_id" in arguments:
                params["project_id"] = arguments["project_id"]

            response = await api_request(
                "GET",
                "https://api.todoist.com/rest/v2/sections",
                headers=headers,
                params=params
            )

            sections = response.json()
            result = f"Found {len(sections)} sections:\n\n"
            for section in sections:
                result += f"• {section['name']}\n"
                result += f"  ID: {section['id']}, Project ID: {section['project_id']}\n"

            return [TextContent(type="text", text=result)]
    
        elif name == "get_labels":
            response = await api_request(
                "GET",
                "https://api.todoist.com/rest/v2/labels",
                headers=headers
            )

            labels = response.json()
            result = f"Found {len(labels)} labels:\n\n"
            for label in labels:
                result += f"• {label['name']}"
                if label.get('color'):
                    result += f" (Color: {label['color']})"
                result += f"\n  ID: {label['id']}\n"

            return [TextContent(type="text", text=result)]
    
        elif name == "get_comments":
            params = {}
            if "task_id" in arguments:
                params["task_id"] = arguments["task_id"]
            elif "project_id" in arguments:
                params["project_id"] = arguments["project_id"]
            else:
                return [TextContent(type="text", text="Error: Must provide either task_id or project_id")]

            response = await api_request(
                "GET",
                "https://api.todoist.com/rest/v2/comments",
                headers=headers,
                params=params
            )

            comments = response.json()
            result = f"Found {len(comments)} comments:\n\n"
            for comment in comments:
                result += f"• {comment['content']}\n"
                result += f"  Posted: {comment.get('posted_at', 'N/A')}\n"

            return [TextContent(type="text", text=result)]
    
        elif name == "create_task":
            # Validate content
            if not arguments.get("content") or not arguments["content"].strip():
                return [TextContent(type="text", text="Error: Task content cannot be empty")]

            # Validate priority if provided
            if "priority" in arguments:
                if not validate_priority(arguments["priority"]):
                    return [TextContent(type="text", text="Error: Priority must be between 1 (normal) and 4 (urgent)")]

            headers["Content-Type"] = "application/json"

            payload = {
                "content": arguments["content"]
            }

            if "project_id" in arguments:
                payload["project_id"] = arguments["project_id"]
            if "section_id" in arguments:
                payload["section_id"] = arguments["section_id"]
            if "due_date" in arguments:
                payload["due_date"] = arguments["due_date"]
            if "priority" in arguments:
                payload["priority"] = arguments["priority"]
            if "labels" in arguments:
                payload["labels"] = arguments["labels"]

            response = await api_request(
                "POST",
                "https://api.todoist.com/rest/v2/tasks",
                headers=headers,
                json=payload
            )

            task = response.json()
            return [TextContent(
                type="text",
                text=f"✅ Task created successfully!\n\nContent: {task['content']}\nID: {task['id']}\nProject ID: {task.get('project_id')}"
            )]
    
        elif name == "update_task":
            # Validate task_id
            if not validate_task_id(arguments.get("task_id", "")):
                return [TextContent(type="text", text="Error: Task ID is required and cannot be empty")]

            # Validate priority if provided
            if "priority" in arguments:
                if not validate_priority(arguments["priority"]):
                    return [TextContent(type="text", text="Error: Priority must be between 1 (normal) and 4 (urgent)")]

            headers["Content-Type"] = "application/json"
            task_id = arguments["task_id"]

            payload = {}
            if "content" in arguments:
                if not arguments["content"].strip():
                    return [TextContent(type="text", text="Error: Task content cannot be empty")]
                payload["content"] = arguments["content"]
            if "due_date" in arguments:
                payload["due_date"] = arguments["due_date"]
            if "priority" in arguments:
                payload["priority"] = arguments["priority"]

            response = await api_request(
                "POST",
                f"https://api.todoist.com/rest/v2/tasks/{task_id}",
                headers=headers,
                json=payload
            )

            task = response.json()
            return [TextContent(
                type="text",
                text=f"✅ Task updated successfully!\n\nContent: {task['content']}\nID: {task['id']}"
            )]
    
        elif name == "complete_task":
            # Validate task_id
            if not validate_task_id(arguments.get("task_id", "")):
                return [TextContent(type="text", text="Error: Task ID is required and cannot be empty")]

            task_id = arguments["task_id"]
            response = await api_request(
                "POST",
                f"https://api.todoist.com/rest/v2/tasks/{task_id}/close",
                headers=headers
            )

            return [TextContent(type="text", text=f"✅ Task {task_id} marked as complete!")]
    
        elif name == "delete_task":
            # Validate task_id
            if not validate_task_id(arguments.get("task_id", "")):
                return [TextContent(type="text", text="Error: Task ID is required and cannot be empty")]

            task_id = arguments["task_id"]
            response = await api_request(
                "DELETE",
                f"https://api.todoist.com/rest/v2/tasks/{task_id}",
                headers=headers
            )

            return [TextContent(type="text", text=f"✅ Task {task_id} deleted successfully!")]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=f"API Error ({e.response.status_code}): {e.response.text}")]
    except httpx.TimeoutException:
        return [TextContent(type="text", text="Error: Request timed out. Please try again.")]
    except httpx.HTTPError as e:
        return [TextContent(type="text", text=f"HTTP Error: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]

async def main():
    """Main entry point for the MCP server"""
    global api_client
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    finally:
        # Cleanup: close the HTTP client
        if api_client is not None:
            await api_client.aclose()

if __name__ == "__main__":
    asyncio.run(main())