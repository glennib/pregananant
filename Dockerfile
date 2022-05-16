FROM python:3.10.4

RUN apt-get update -qq
RUN apt-get install -y iputils-ping iproute2
RUN apt-get install -y sudo


RUN pip install Pillow
RUN pip install pandas
RUN pip install pysimplegui
RUN pip install black

ARG GID=1000
ARG UID=1000

RUN groupadd -g ${GID} -o user
RUN useradd -m -u ${UID} -g ${GID} -o -s /bin/bash user
RUN mkhomedir_helper user
RUN echo "user:user" | chpasswd
RUN adduser user sudo
USER user

ENV PYTHONPATH=/workspaces/pregananant/modules:$PYTHONPATH
