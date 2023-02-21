FROM ubuntu:latest
ADD . /app
WORKDIR /app
RUN apt-get update && \
    apt-get install -y python3 python3-pip wget && pip install argon2-cffi PyMySQL

RUN python3 install-docker.py
# wget https://raw.githubusercontent.com/Cantina-Org/Cloud/master/install.py && python3 install.py
