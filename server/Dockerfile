# Dockerfile
# ──────────────────────────────────────────────────────────────
# This packages your Mumbai environment server into a container.
#
# How it works:
#   FROM    → start with an official Python image (clean Linux + Python)
#   WORKDIR → set /app as the working directory inside the container
#   COPY    → copy your project files into the container
#   RUN     → install your Python dependencies
#   EXPOSE  → tell Docker this app uses port 8000
#   CMD     → the command that runs when the container starts
# ──────────────────────────────────────────────────────────────

# Use official Python 3.11 slim image (smaller than full Python image)
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements first (Docker caches this layer — speeds up rebuilds)
COPY requirements.txt .

# Install all Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your project files into the container
COPY . .

# Tell Docker that this container listens on port 8000
EXPOSE 8000

# Command to start the server when the container runs
# Uses 0.0.0.0 so it's accessible from outside the container (not just localhost)
CMD ["python", "-m", "uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]