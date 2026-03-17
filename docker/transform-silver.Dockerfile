FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH=/mnt/data/sentinel-pi
CMD ["python", "/mnt/data/sentinel-pi/src/transform_knmi_to_silver.py"]
