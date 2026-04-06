FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# HF Spaces uses port 7860
EXPOSE 7860

# Run Streamlit app (it starts FastAPI internally on 7861)
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]