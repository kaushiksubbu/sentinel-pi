FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH=/mnt/data/sentinel-pi/src:/mnt/data/sentinel-pi/src/common_func:/mnt/data/sentinel-pi/src/ingest_to_bronze
CMD ["python", "/mnt/data/sentinel-pi/src/ingest_to_bronze/load_knmi_to_bronze.py"]