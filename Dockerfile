# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the server code
COPY server.py .

# Copy additional files if needed
COPY README.md .

# Expose port (Smithery will set PORT environment variable)
ENV PORT=8081
EXPOSE $PORT

# Run the server
CMD ["python", "server.py"]
