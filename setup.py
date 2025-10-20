from setuptools import setup, find_packages

setup(
    name="todoist-mcp-server",
    version="1.0.0",
    description="MCP server to connect Todoist with Claude through REST API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="shawkatdidar",
    url="https://github.com/shawkatdidar/todoist_claude_mcp_server_v1.0",
    py_modules=["server"],
    install_requires=[
        "httpx>=0.27.0",
        "python-dotenv>=1.0.0",
        "mcp>=0.1.0",
        "tenacity>=8.2.0",
    ],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "todoist-mcp-server=server:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="todoist mcp claude api productivity task-management",
)
