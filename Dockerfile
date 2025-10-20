# Use UV-based Python image for faster builds
FROM ghcr.io/astral-sh/uv:python3.12-alpine

# Set working directory
WORKDIR /app

# Enable bytecode compilation for better performance
ENV UV_COMPILE_BYTECODE=1

# Copy dependency files
COPY pyproject.toml ./
COPY requirements.txt ./

# Install dependencies using UV
RUN uv pip install --system --no-cache -r requirements.txt

# Copy application code
COPY server.py ./
COPY README.md ./

# Smithery sets PORT environment variable to 8081
ENV PORT=8081

# Run the server
CMD ["python", "server.py"]
