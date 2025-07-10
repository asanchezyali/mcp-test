FROM python:3.12-slim AS base
WORKDIR /app
RUN pip install uv
COPY pyproject.toml .
RUN uv pip install --system .
COPY server.py .
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production
EXPOSE 8000
USER nobody:nogroup
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8100", "--workers", "4"] 