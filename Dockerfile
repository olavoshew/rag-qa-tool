FROM python:3.11-slim

RUN useradd -m -u 1000 user

WORKDIR /app

COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=user . .

RUN mkdir -p /app/data/chroma /app/data/uploads && chown -R user:user /app/data

USER user

ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONPATH=/app

EXPOSE 7860

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "7860"]
