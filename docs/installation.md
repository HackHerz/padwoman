# Installation

## Docker

There is a Dockerfile in the root directory.

## Example nginx Configuration

A minimal nginx configuration if you are running everything inside a Docker stack.


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

