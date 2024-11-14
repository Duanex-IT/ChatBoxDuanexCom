# syntax=docker/dockerfile:1

FROM python:3.10-slim-buster

WORKDIR /flask_app

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

ENV FLASK_APP=flask_api.py

EXPOSE 5000

CMD [ "flask", "run", "--host=0.0.0.0", "--port=5000"]
