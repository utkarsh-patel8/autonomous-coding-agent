FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/workspace

RUN pip install --no-cache-dir pytest

WORKDIR /workspace

CMD ["sh"]