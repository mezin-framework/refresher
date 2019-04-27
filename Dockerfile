
FROM python:2.7

WORKDIR /var/app/

COPY . /var/app/refresher

WORKDIR /var/app/refresher

RUN pip install -r requirements.txt