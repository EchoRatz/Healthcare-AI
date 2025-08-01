FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ src/
COPY scripts/ scripts/
COPY data/ data/
COPY pyproject.toml .

# Install package
RUN pip install -e .

# Create data directories
RUN mkdir -p data/cache data/output

EXPOSE 8000

CMD ["python", "scripts/interactive_qa.py"]
