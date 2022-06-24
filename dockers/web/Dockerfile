# syntax=docker/dockerfile:1
FROM python:3.8
RUN apt update && apt install -y python3-dev gcc libffi-dev libzbar-dev
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY ./requirements/base.txt requirements.txt
RUN pip install -r requirements.txt
COPY ./dockers/web/run_web.sh /run_web.sh
RUN chmod a+rwx /run_web.sh && chmod -R a+rwx /code
COPY . /code/