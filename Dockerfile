FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY parser.py .
COPY excel_data.py .

CMD ["python", "excel_data.py"]
