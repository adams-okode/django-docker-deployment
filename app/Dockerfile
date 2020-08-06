# pull official base image
# run app settings
FROM python:3.7.4-alpine
# set work directory
WORKDIR /usr/src/app
# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN apk add --update --no-cache mariadb-connector-c-dev \
    && apk add --no-cache --virtual .build-deps \
    mariadb-dev \
    gcc \
    musl-dev \
    && pip install mysqlclient==1.4.2.post1 \
    && apk del .build-deps \
    && apk add libffi-dev openssl-dev libgcc 
RUN apk add python python-dev py2-pip autoconf automake g++ make --no-cache
RUN apk add --no-cache jpeg-dev zlib-dev
RUN apk add gcc musl-dev
# RUN pip install cryptography --no-binary cryptography
# install dependencies
RUN pip install --upgrade pip gunicorn 
RUN pip install bcrypt==3.1.2
RUN pip install environs

COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt
# copy entrypoint.sh
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh
# copy project
COPY . /usr/src/app/
#Gie Permission and make executable
RUN chmod 755 /usr/src/app/entrypoint.sh
RUN ["chmod", "+x", "/usr/src/app/entrypoint.sh"]
# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
