FROM python:3.10.4

RUN apt-get update -qq && apt-get install -y \
    iputils-ping

RUN pip install Pillow
RUN pip install pandas
RUN pip install pysimplegui
RUN pip install black

ENV PYTHONPATH=/workspaces/pregananant/modules:$PYTHONPATH
