###########
# BUILDER #
###########

ARG PYTHON_DOCKER_TAG=3.11-slim-bookworm

# pull official base image
FROM python:${PYTHON_DOCKER_TAG} AS builder

# set work directory
WORKDIR /usr/src/django_app/

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# install system dependencies
RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y --no-install-recommends gcc git python3-dev build-essential pkg-config default-libmysqlclient-dev

# install python dependencies
COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/django_app/wheels -r requirements.txt

#########
# FINAL #
#########

# pull official base image
FROM python:${PYTHON_DOCKER_TAG}

# install dependencies
RUN echo "deb http://deb.debian.org/debian/ unstable main contrib non-free" > /etc/apt/sources.list
RUN apt-get update
RUN apt-get install -y --no-install-recommends gdal-bin libgdal-dev

COPY --from=builder /usr/src/django_app/wheels /wheels
RUN pip install --no-cache /wheels/*

# create the app user
RUN adduser --system --group --home /home/app app

# change to the app user
USER app

# create the appropriate directories
ENV APP_HOME=/home/app/web
RUN mkdir -p $APP_HOME/writable/media
RUN mkdir $APP_HOME/staticfiles
RUN mkdir $APP_HOME/tmp
WORKDIR $APP_HOME

# copy project
COPY . $APP_HOME