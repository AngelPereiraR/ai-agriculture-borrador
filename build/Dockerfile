# Stage 1: install dependencies
FROM python:3.13-slim AS deps
WORKDIR /tmp/deps
ENV PYTHONUNBUFFERED=1
COPY ./requirements.txt .
RUN pip install --prefix /install -r requirements.txt

# Stage 2: runtime image with app code
FROM python:3.13-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /workspace/ai-agriculture
COPY --from=deps /install /usr/local
COPY ./src .
CMD ["python3", "/workspace/ai-agriculture/manage.py", "runserver", "0.0.0.0:8000"]
