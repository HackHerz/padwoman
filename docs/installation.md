# Installation

The recommended way for installation is Docker. If you wish you can also install Padwoman without Docker.
Either way Padwoman needs a configuration file `settings.yml` in the same directory it is executed in. The configuration itself is documented [here](/config/).

Besides Padwoman itself you'll need need a working installation of [etherpad lite](https://github.com/ether/etherpad-lite) and [redis](https://redis.io/) (for caching, currently there is no other option implemented).

## Without Docker

To allow for better performance Padwoman is capable of running as an wsgi Application via gunicorn or uwsgi.

```bash
$ uwsgi --http 0.0.0.0:8000 --wsgi-file wsgi.py --master --processes 4 --threads 2 --disable-logging
```

Please remember to install all the necessary dependencies which are specified in the `requirements.txt`.


## Docker

There is a Dockerfile in the root directory, which you can either build yourself or use the image from the Docker Hub [https://hub.docker.com/r/hackherz/padwoman](https://hub.docker.com/r/hackherz/padwoman).

Please remember to mount the configuration file to `/usr/src/app/settings.yml` inside the Container.


### Example docker-compose

```yaml
version: '3'
services:
  padwoman:
    image: hackherz/padwoman
    restart: unless-stopped
    volumes:
      - ./settings.yml:/usr/src/app/settings.yml
      - /etc/localtime:/etc/localtime:ro
    ports:
      - 8000:8000

  redis:
    restart: unless-stopped
    image: redis:alpine
    volumes:
      - /etc/localtime:/etc/localtime:ro
```



## Example nginx Configuration

To run everything behind a reverse proxy you'll need to configure certain paths accordingly.
This allows for a seamless integration of both services.
When running padwoman behind a reverse proxy make sure to set the http interface to the loopback address to prevent direct access (`uwsgi -http 127.0.0.1:8000` for uwsgi).


```nginx
server {
	listen 80;
	server_name pads.tld;

	# Padwoman
	location / {
		proxy_pass http://padwoman:8000/;
	}

	# Etherpad
	location ~ /(p/|admin/|static/|socket.io/|javascripts/|jserror|locales|locales.json|pluginfw) {
		proxy_pass http://etherpad:9001/;
	}
}
```

## Example systemd configuration

To run padwoman as a service using systemd, the following unit file can be used. Change the working directory to point to the location where you've installed padwoman as well as the user and group. In the example uwsgi is used for the wsgi server.

```ini
[Unit]
Description=Padwoman etherpad organizer
After=syslog.target network.target

[Service]
Type=notify
User=etherpad
Group=etherpad
WorkingDirectory=/path/to/padwoman
ExecStart=uwsgi --http 127.0.0.1:8000 --wsgi-file wsgi.py --master --processes 4 --threads 2 --disable-logging --die-on-term
Restart=always
StandardOutput=append:/var/log/padwoman.log
StandardError=append:/var/log/padwoman.err.log

[Install]
WantedBy=multi-user.target
```

