FROM python:3.10-slim

# Hugging Face Spaces runs containers as user 1000 and expects port 7860.
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH
WORKDIR /home/user/app

COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download the local embedding model at build time so it is not fetched on every start.
RUN python -c "from chromadb.utils.embedding_functions import DefaultEmbeddingFunction as D; D()(['warmup'])"

COPY --chown=user . .

EXPOSE 7860
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "7860"]
