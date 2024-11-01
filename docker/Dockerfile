FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements /app/requirements

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements/prod.txt

COPY ./app /app
COPY ./.env /.env
COPY ./fastapi_telethon_session.session /app/fastapi_telethon_session.session

EXPOSE 80

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
