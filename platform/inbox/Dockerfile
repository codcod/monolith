# syntax=docker/dockerfile:1

#
# COMPILE
#
FROM python:3-alpine AS compile-image
RUN apk --update --no-cache add gcc build-base

RUN python -m venv /opt/venv
ENV PATH "/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#
# BUILD
#
FROM python:3-alpine AS build-image
COPY --from=compile-image /opt/venv /opt/venv

RUN apk add --no-cache tzdata
ENV TZ=Europe/Warsaw

WORKDIR /opt/stelo
COPY . .

EXPOSE 8080

ENV PATH "/opt/venv/bin:$PATH"
CMD PYTHONPATH=. ./bin/stelo-inbox ./config/config.toml