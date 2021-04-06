FROM ubuntu:20.04

RUN mkdir /source
COPY . /source
RUN cd /source
RUN sh install.sh
RUN sh run.sh