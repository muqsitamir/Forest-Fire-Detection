# Deployment Guide
## Domain Setup
### Domain Provider
**PKNIC** 
- login url: https://pk6.pknic.net.pk/pk5/login.PK
- login username: heritage360
- login password: {ask your supervisor}

### Linode Domain Setup

#### Credentials

- url: https://login.linode.com/login
- username: tpi
- password: {ask your supervisor}

1. Login to Linode account.
2. Go to Domains tab in the side menu.
3. Create a new domain by the name of your PKNIC domain.
4. Set up A/AAAA Record (Hostname: @, IP: {your linode server's ip address})
5. Set the name of your NS record (Name Records) in your Domain settings in PKNIC account.

### NGINX Setup

*Reference*: https://ubuntu.com/tutorials/install-and-configure-nginx#1-overview

#### Steps

1. Install NGINX: `sudo apt update && sudo apt install nginx`
2. Create a new NGINX configuration: `nano /etc/nginx/sites-available/wwf_lums.conf`
3. Paste the following contents into the file created in step 2.
``` 
# the upstream component nginx needs to connect to
upstream django {
    server unix:///tmp/wwf_lums.sock; # for a file socket
    # server 0.0.0.0:6800; # for a web port socket (we'll use this first)
}

server {
    # the port your site will be served on
    server_name tpilums.org.pk;
    # the domain name it will serve for
    # substitute your machine's IP address or FQDN
    charset     utf-8;

    # max upload size
    client_max_body_size 75M;
    
    location /media  {
        alias /root/wwf_snow_leopard/media;  # your Django project's media files - amend as required
    }

    location /static {
        alias /root/wwf_snow_leopard/staticfiles; # your Django project's static files - amend as required
    }
    
    location / {
        uwsgi_pass django;
        # the uwsgi_params file you installed
        include /etc/nginx/uwsgi_params;
    }
}

```
### Setup UWSGI

1. Install UWSGI module: `pip install uwsgi`
2. Create a new file: `nano /etc/uwsgi/wwf_lums.ini`
3. Paste the following contents into the file created in step 2: 
```
[uwsgi]
virtualenv=/root/wwf_snow_leopard/venv/
uid = www-data
gid = www-data
chmod-socket = 664
processes = 4
master = true
threads = 4
env = DJANGO_SETTINGS_MODULE=backend.settings
module = backend.wsgi
chdir = wwf_snow_leopard
socket = /tmp/wwf_lums.sock
logto = /var/log/uwsgi/access.log
#http = :8080
daemonize = /var/log/uwsgi/access.log
safe-pidfile = /tmp/safe-pidfile.pid
#chmod-socket = 666
```

#### Passing Parameters/Requests from NGINX to UWSGI

4. Create a new file: `nano /etc/nginx/uwsgi_params`
5. Paste the following contents into the file created in step 4.
```
uwsgi_param  QUERY_STRING       $query_string;
uwsgi_param  REQUEST_METHOD     $request_method;
uwsgi_param  CONTENT_TYPE       $content_type;
uwsgi_param  CONTENT_LENGTH     $content_length;

uwsgi_param  REQUEST_URI        $request_uri;
uwsgi_param  PATH_INFO          $document_uri;
uwsgi_param  DOCUMENT_ROOT      $document_root;
uwsgi_param  SERVER_PROTOCOL    $server_protocol;
uwsgi_param  REQUEST_SCHEME     $scheme;
uwsgi_param  HTTPS              $https if_not_empty;

uwsgi_param  REMOTE_ADDR        $remote_addr;
uwsgi_param  REMOTE_PORT        $remote_port;
uwsgi_param  SERVER_PORT        $server_port;
uwsgi_param  SERVER_NAME        $server_name;

```
