FROM ubuntu:latest
WORKDIR /app
RUN apt-get update && \
    apt-get install -y python3 python3-pip wget && pip install argon2-cffi PyMySQL

RUN wget https://raw.githubusercontent.com/Cantina-Org/Cloud/master/install.py && python3 install.py
