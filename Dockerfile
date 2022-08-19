FROM python:3.10.4

RUN apt-get update -qq \
    && apt-get install -y -qq \
        iputils-ping \
        iproute2 \
        sudo \
        vim \
        fonts-open-sans \
        tree \
    && apt-get clean -qq

RUN pip install \
    Pillow \
    pandas \
    pysimplegui \
    black \
    moviepy

ARG GID=1000
ARG UID=1000

RUN groupadd -g ${GID} -o user
RUN useradd -m -u ${UID} -g ${GID} -o -s /bin/bash user
RUN mkhomedir_helper user
RUN echo "user:user" | chpasswd
RUN adduser user sudo
USER user

ENV PYTHONPATH=/workspaces/pregananant/modules:$PYTHONPATH
