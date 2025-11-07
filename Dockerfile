FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

ENV FLASK_RUN_RELOAD=true

CMD ["python", "server.py"]