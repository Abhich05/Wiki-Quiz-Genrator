FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements_prod.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements_prod.txt

# Copy application code
COPY main.py .
COPY .env.example .

# Create .env file if it doesn't exist (will use environment variables)
RUN touch .env

# Expose port
EXPOSE 8000

# Set environment variables
ENV PORT=8000
ENV HOST=0.0.0.0

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/')" || exit 1

# Run the application
CMD ["python", "main.py"]
