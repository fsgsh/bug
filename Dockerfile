FROM debian:latest

RUN apt update && apt upgrade -y
RUN apt install git python3-pip ffmpeg -y

WORKDIR /./
COPY . /./

RUN pip3 install --upgrade pip
RUN pip3 install -U -r requirements.txt

CMD cd bot && python3 main.py
