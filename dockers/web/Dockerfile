# syntax=docker/dockerfile:1
FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY ./requirements/base.txt requirements.txt
RUN pip install -r requirements.txt
COPY ./dockers/web/run_web.sh /run_web.sh
RUN chmod a+rwx /run_web.sh && chmod -R a+rwx /code
COPY . /code/