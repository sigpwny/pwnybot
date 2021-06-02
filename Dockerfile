FROM ubuntu:20.04
COPY . /source

# Separate because it breaks when I use one line
RUN apt update
RUN apt install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt update
RUN apt install -y python3.8
RUN apt-get -y install python3-pip

# Change into the source directory
WORKDIR /bot

# Install requirements
RUN python3 -m pip install -r requirements.txt

