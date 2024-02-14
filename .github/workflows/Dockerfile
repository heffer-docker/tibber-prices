FROM python:3.8-slim
WORKDIR /app
COPY tibber_prices.py .
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "tibber_prices.py"]
