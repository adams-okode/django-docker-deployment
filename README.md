# Deploying Django App Inside Docker container

This tutorial gives a step by step guide on deploying a django project inside a docker container. We'll deploy without a virtual environment however it is best practice to use virtual environment if you’re a python developer because maintaining python packages in one environment is not that easy and there can be huge conflicts.

*Prerequisites*
  - an already existing django project
  - docker/docker-compose is installed
  - a bit of knowledge working with linux/unix systems

### Step 1
Assuming you already have a working django project export all your installed packages to a requirements file i.e. run 

```bash
  pip freeze > requirements.txt
```

### Step 2
Create create a folder www/html within your project copy all your project content into this new folder so that the structure is as shown

```bash
.
├── app
│   ├── db.sqlite3
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── env
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
  create your Dockerfile, docker-compose.yml and sote-config.conf files within the root folder  the final structure should be as shown below;
```
project
└───www
│   └───html
|       └───{ your-django-project }
|           │   ...
|           │   manage.py
|           |   ...
|  docker-compose.yml
|  Dockerfile
|  README.md
|  requirements.txt
|  site-config.conf
```
### Step 3 [ Setting Up Docker]
  First we need to have a docker image that includes our project in order to achieve the deployment in kubernetes. So for that we need a docker file that can do that for us. So here’s the docker file that will do the trick for us

``` docker
FROM ubuntu

RUN apt-get update
RUN apt-get install -y apt-utils vim curl apache2 apache2-utils
RUN apt-get -y install python3 libapache2-mod-wsgi-py3
RUN ln /usr/bin/python3 /usr/bin/python
RUN apt-get -y install python3-pip
RUN ln /usr/bin/pip3 /usr/bin/pip
RUN pip install --upgrade pip
RUN pip install django ptvsd


ADD ./site-config.conf /etc/apache2/sites-available/000-default.conf
ADD ./requirements.txt /var/www/html

WORKDIR /var/www/html
RUN pip install -r requirements.txt

RUN chmod 664 /var/www/html/{ your-site-name }/{ your-site-name }/db.sqlite3
RUN chmod 775 /var/www/html/{ your-site-name }/{ your-site-name }
RUN chown :www-data /var/www/html/{ your-site-name }/{ your-site-name }/db.sqlite3
RUN chown :www-data /var/www/html/{ your-site-name }/{ your-site-name }


EXPOSE 80 3500
CMD ["apache2ctl", "-D", "FOREGROUND"]
```


If SQLITE is not your DB of choice then you are free to remove  the following from your Dockerfile configuration, These essentially give apache wrte permissions to your project database

```docker
RUN chmod 664 /var/www/html/{ your-site-name }/{ your-site-name }/db.sqlite3
RUN chmod 775 /var/www/html/{ your-site-name }/{ your-site-name }
RUN chown :www-data /var/www/html/{ your-site-name }/{ your-site-name }/db.sqlite3
RUN chown :www-data /var/www/html/{ your-site-name }/{ your-site-name }
```
  next we need to modify the docker-compose.yml to:

```yaml
version: "2"

services: 
  django-apache:
    build: .
    container_name: django-deployment
    ports:
      - '8005:80'
      - '3500:3500'
      - '8006:81'
    volumes: 
      - $PWD/www:/var/www/html
```
### Step 4 [ Apache Config ]
modify site-config.conf to read 

```bash
WSGIPythonPath /var/www/html/{ your-site-name }
<VirtualHost *:80>
    # The ServerName directive sets the request scheme, hostname and port that
    # the server uses to identify itself. This is used when creating
    # redirection URLs. In the context of virtual hosts, the ServerName
    # specifies what hostname must appear in the request's Host: header to
    # match this virtual host. For the default virtual host (this file) this
    # value is not decisive as it is used as a last resort host regardless.
    # However, you must set it for any further virtual host explicitly.
    ServerName localhost
    ServerAdmin webmaster@localhost
    DocumentRoot /var/www/html/{ your-site-name }

    Alias /static "/var/www/html/{ your-site-name }/static"

    WSGIScriptAlias / /var/www/html/{ your-site-name }/{ your-site-name }/wsgi.py

    # Available loglevels: trace8, ..., trace1, debug, info, notice, warn,
    # error, crit, alert, emerg.
    # It is also possible to configure the loglevel for particular
    # modules, e.g.
    #LogLevel info ssl:warn

    ErrorLog /var/www/html/{ your-site-name }/logs/error.log
    CustomLog /var/www/html/{ your-site-name }/logs/access.log combined

    # For most configuration files from conf-available/, which are
    # enabled or disabled at a global level, it is possible to
    # include a line for only one particular virtual host. For example the
    # following line enables the CGI configuration for this host only
    # after it has been globally disabled with "a2disconf".
    #Include conf-available/serve-cgi-bin.conf
</VirtualHost>
```

### Step 5 [ Deployment ]
For this step  you need to have both docker and docker compose installed on your server or local computer.

You can find the tutorial on
[docker windows][1], [docker mac][2], [docker linux (Debian and Ubuntu)][3]  and [ docker compose ][4]

[1]: https://docs.docker.com/docker-for-windows/install/ "Docker windows Set up "
[2]: https://docs.docker.com/docker-for-mac/ "Docker mac Set up "
[3]: https://runnable.com/docker/install-docker-on-linux "Docker linux Set up "
[4]: https://docs.docker.com/compose/install/ "Docker Compose Install"

If all this is set up then navigate to your project folder within your specific CLI 
and run 
```bash
    docker-compose up --build
```
the above command will build and deploy the image to the defined stack, once the container is up and running open http://{ your-ip }:8005/ to access your application

> **Note** : remember to run collectstatic command on your django project so as to generate all static files. This is because Apache will has ana alias /static that points to the static folder within your app. This requires the folder to contain all your statically generated files before hand. <br> Alternatively you can embed a RUN function within your Dockerfile so that all static file are automatically generated everytime the image is built.   

### Remarks
To help you manage your docker environment you can install [Portainer][5] a Docker GUI management center.

[5]: https://www.portainer.io/installation/ "Portainer Set up"








  






