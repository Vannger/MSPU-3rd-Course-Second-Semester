FROM python:3.10-slim

WORKDIR /PAPKI.NET/

COPY requirements.txt .

RUN pip install --no-cache-dir -r  requirements.txt

COPY . .

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

