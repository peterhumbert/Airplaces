#use an official Python runtime as a parent image
FROM python:3.6.2-slim

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt

EXPOSE 80

CMD ["python", "app.py"]
