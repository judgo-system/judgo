# syntax=docker/dockerfile:1
FROM python:3.8
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY ./requirements/local.txt requirements.txt
RUN pip install -r requirements.txt
COPY ./docker/run_web.sh /run_web.sh
RUN chmod a+rwx /run_web.sh && chmod -R a+rwx /code
COPY . /code/