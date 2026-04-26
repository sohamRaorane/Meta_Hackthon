FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (this layer is cached by Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files into the container
COPY . .

# Hugging Face Spaces uses port 7860
EXPOSE 7860

# Serve Streamlit on the public Space port and keep FastAPI backend internal.
CMD ["sh", "-c", "uvicorn server.app:app --host 0.0.0.0 --port 8000 & streamlit run app_demo.py --server.address 0.0.0.0 --server.port 7860 --server.headless true"]
