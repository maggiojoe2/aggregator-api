FROM python:3.6-alpine3.7 as builder
COPY requirements.txt requirements.txt
RUN apk add --no-cache --update \
    build-base \
    && pip install --upgrade pip \
    && pip install -r requirements.txt

FROM builder as developer
COPY . /usr/app
WORKDIR /usr/app
CMD python3.6 -m sanic aggregator.aggregator.app --host=0.0.0.0 --port=8080 --debug