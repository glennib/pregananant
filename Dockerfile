FROM python:3.10.4

RUN apt-get update -qq && apt-get install -y \
    iputils-ping

WORKDIR /tmp/build
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt
