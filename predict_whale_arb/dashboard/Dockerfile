FROM python:3.12-slim
WORKDIR /app
COPY . /app/predict_whale_arb
RUN pip install --no-cache-dir -r /app/predict_whale_arb/requirements.txt -r /app/predict_whale_arb/dashboard/backend/requirements.txt
ENV PYTHONPATH=/app/predict_whale_arb
ENV DEMO_MODE=true
EXPOSE 8080
CMD ["uvicorn","dashboard.backend.app:app","--host","0.0.0.0","--port","8080"]
