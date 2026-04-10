FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH=/mnt/data/sentinel-pi/src:/mnt/data/sentinel-pi/src/common_func:/mnt/data/sentinel-pi/src/ingest_to_gold:/mnt/data/sentinel-pi/src/lineage
CMD ["python", "/mnt/data/sentinel-pi/src/ingest_to_gold/transform_silver_to_gold.py"]