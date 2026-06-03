FROM python:3.10-slim

RUN addgroup --gid 1000 appuser && adduser --uid 1000 --gid 1000 --disabled-password --gecos "" appuser

WORKDIR /Papki.net/

COPY requirements.txt .

RUN pip install --no-cache-dir -r  requirements.txt

COPY . .

RUN chown -R appuser:appuser /Papki.net/

USER appuser

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

