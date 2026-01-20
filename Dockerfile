FROM python:3.11-slim

# setam directorul de lcuruu in container
WORKDIR /app

COPY requirements.txt .

# instalam toate dependentile
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

CMD ["python", "main.py"] 