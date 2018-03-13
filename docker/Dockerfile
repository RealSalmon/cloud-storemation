FROM python:alpine3.6

ENV PYTHONPATH=/home/app/python
ENV AWS_DEFAULT_REGION=us-east-1

RUN addgroup app && adduser -S app -G app && \
    apk add --update-cache --virtual .build-deps gcc \
                                                 musl-dev \
                                                 libffi-dev \
                                                 openssl-dev && \
    pip install --no-cache-dir pytest \
                               pytest-cov \
                               moto \
                               boto3==1.5.8 \
                               botocore==1.8.22 && \
    apk del .build-deps && rm -rf /var/cache/apk/*

USER app
WORKDIR /home/app
