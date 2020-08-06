# Deploying Django App Inside Docker container

This is a step-by-step tutorial that details how to configure Django to run on Docker with Postgres. For production environments, we'll add on Nginx and Gunicorn. We'll also take a look at how to serve Django static and media files via Nginx.

*Prerequisites*
  - docker/docker-compose installed
  - a bit of knowledge working with linux/unix systems

### Step 1
Create new project 
```bash
$ mkdir django-on-docker && cd django-on-docker
$ mkdir app && cd app
$ python3.8 -m venv env
$ source env/bin/activate
(env)$ pip install django==3.0.7
(env)$ django-admin.py startproject testapp .
(env)$ python manage.py migrate
(env)$ python manage.py runserver
```

```bash
pip freeze > requirements.txt
```

modify your application to allow it read imformation directly from the environment this will help you manage deployment on multiple sites without having to rebiuld image. For this use [environs][6] 

[6]: https://pypi.org/project/environs/ "Environs"

modify your settings.py to 

```python
env = Env() # add this to top
env.read_env()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = eval(env('DEBUG'))


DATABASES = {
    'default': {
        'ENGINE': env('DB_ENGINE'),
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
        'OPTIONS': {
            'connect_timeout': 600,
        }
    }
}
```

For testing create a .env file with the following paramenters
```bash
DB_ENGINE=django.db.backends.mysql
DB_NAME=YOUR-DB
DB_USER=YOUR-USER
DB_PASSWORD=YOUR-PASSOWRD
DB_HOST=YOUR-HOST
DB_PORT=3306

DEBUG=True
PWD=plIJi2z3jyS2bGcz
```

### Step 3 [ Setting Up Docker]
First we need to have a docker image that includes our project in order to achieve the deployment. So for that we need a docker file that will do this for us. So here’s the docker file that will do the trick for us

```docker
# pull official base image
# run app settings
FROM python:3.7.4-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set up packages required for mysql connector
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

# pre install dependencies
RUN pip install --upgrade pip gunicorn 
RUN pip install bcrypt==3.1.2
RUN pip install environs

COPY ./requirements.txt /usr/src/app/requirements.txt

# Install all packaged
RUN pip install -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

# copy project
COPY . /usr/src/app/

# Give Permission and make executable
RUN chmod 755 /usr/src/app/entrypoint.sh

RUN ["chmod", "+x", "/usr/src/app/entrypoint.sh"]

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
```


### Step 4 [ Nginx Config ]
Nginx is used as a proxy and exposes the application assets to the outside network.

### Step 2 [ Structure Set up]
create an nginx folder, this will hold server configs and files.
The final structure is as below

```bash
├── app
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── manage.py
│   ├── requirements.txt
│   ├── static
│   ├── testapp
│   └── web
├── docker-compose.yml
├── mysql
│   └── init.sql
├── nginx
│   ├── Dockerfile
│   └── nginx.conf
└── README.md
```

Within the nginx folder create a nginx.conf file and add the following

```bash
upstream appsite {
    server web:3762;
}

server {

    listen 80;

    client_max_body_size 14M;

    location / {
        proxy_pass http://appsite;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_redirect off;
    }

    location /static/ {
        alias /usr/src/app/static/;
    }

    location /media/ {
        alias /usr/src/app/media/;
    }

}
```

Create docker file to define  set up of proxy image

```docker
FROM nginx:1.17.2-alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY ./nginx.conf /etc/nginx/conf.d
```

### Step 5 [ Deployment ]
For this step  you need to have both docker and docker compose installed on your server or local computer.

You can find the tutorial on
[docker windows][1], [docker mac][2], [docker linux (Debian and Ubuntu)][3]  and [ docker compose ][4]

[1]: https://docs.docker.com/docker-for-windows/install/ "Docker windows Set up "
[2]: https://docs.docker.com/docker-for-mac/ "Docker mac Set up "
[3]: https://runnable.com/docker/install-docker-on-linux "Docker linux Set up "
[4]: https://docs.docker.com/compose/install/ "Docker Compose Install"

create mysql folder within project with init.sql file to create tables within the DB image

define your docker-compose ochestration file(docker-compose.yml)
```yaml
version: "3.3"

services:
  web:
    container_name: website.testapp.application
    build: ./app
    command: gunicorn testapp.wsgi:application --bind 0.0.0.0:3762
    volumes:
      - ./app/static:/usr/src/app/static
      - media_volume:/usr/src/app/media
    expose:
      - "3762"
    env_file: .env
    depends_on:
      - mysql
    networks:
      local_network:
        ipv4_address: 172.28.1.4

  nginx:
    container_name: website.testapp.proxy
    build: ./nginx
    volumes:
      - ./app/static:/usr/src/app/static
      - media_volume:/usr/src/app/media
    ports:
      - "1338:80"
    depends_on:
      - web
    networks:
      local_network:
        ipv4_address: 172.28.1.3

  mysql:
    image: mysql:latest
    container_name: website.tutorial.mysql
    volumes:
      - db_data:/var/lib/mysql:rw
      - ./mysql/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    environment:
      MYSQL_USER: ${DB_USER}
      MYSQL_PASSWORD: ${DB_PASSWORD}
      MYSQL_ROOT_PASSWORD: ${DB_PASSWORD}
      MYSQL_DATABASE: ${DB_NAME}
    ports:
      - "3306:3306"
    networks:
      local_network:
        ipv4_address: ${DB_HOST}

volumes:
  static_volume:
  media_volume:
  db_data:

networks:
  local_network:
    ipam:
      driver: default
      config:
        - subnet: 172.28.0.0/16
```
If all this is set up then navigate to your project folder within your specific CLI 
and run 
```bash
docker-compose up -d --build
```
the above command will build and deploy the image to the defined stack, once the container is up and running open http://{ your-ip }:1338/ to access your application

> **Note** : remember to run collectstatic command on your django project so as to generate all static files. This is because Nginx will has an alias /static that points to the static folder within your app. This requires the folder to contain all your statically generated files before hand. <br> Alternatively you can embed a RUN function within your Dockerfile so that all static files are automatically generated everytime the image is built.   

### Remarks
In this tutorial, we walked through how to containerize a Django web application with MySQL for development. We also created a production-ready Docker Compose file that adds Gunicorn and Nginx into the mix to handle static and media files. You can now test out a production setup locally.


For an actual production deployment site:
- You may want to use a fully managed database service -- like RDS or Cloud SQL -- rather than managing your own MySQL instance within a container.
- Non-root user for the db and nginx services


To help you manage your docker environment you can install [Portainer][5] a Docker GUI management center.

[5]: https://www.portainer.io/installation/ "Portainer Set up"

Full project to get you started can be found @[repo][7]

[7]: https://github.com/adams-okode/django-docker-deployment "DeployingDjango App Inside Docker container"








  






