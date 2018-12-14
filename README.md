#Web Hook Forwarder
The idea is to run local commands on internal servers using SSH if you have external webhooks triggering it.
The implementation currently runs the docker compose chain for updating existing images.
This stupid simple setup assumes a test server hosting frontend and backed, acceptance frontend and backend.

##Configure
Create a ssh config file in /etc/ssh/ssh_config and add the following entries: 
1. Test server hosting both frontend and backend: `test`
2. Acceptance server hosting frontend: `acc-fe`
3. Acceptance server hosting backend: `acc-be`

```bash
Host <hostname should match entries above>
    HostName <ip address of internal development machine>
    User <user that can execute docker-compose>
    IdentityFile <path to the private key file for the specified user>
```

##Install
####NGINX
```bash
sudo apt install nginx
```
/etc/nginx/nginx.conf
```bash
server {
    location / {
        include uwsgi_params;
        uwsgi_pass unix:///tmp/uwsgi.sock;
    }
}
```

####uWSGI
```bash
sudo pip install uwsgi
```
/etc/uwsgi/wsgi.ini
```ini
[uwsgi]
socket = /tmp/uwsgi.sock
chown-socket = nginx:nginx
chmod-socket = 664
hook-master-start = unix_signal:15 gracefully_kill_them_all
```

####Supervisord
```bash
sudo apt install supervisord
```
/etc/supervisor/conf.d/supervisord.conf
```ini
[supervisord]
nodaemon=true

[program:uwsgi]
command=/usr/local/bin/uwsgi --ini /etc/uwsgi/uwsgi.ini --die-on-term --need-app
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0

[program:nginx]
command=/usr/sbin/nginx
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
# Graceful stop, see http://nginx.org/en/docs/control.html
stopsignal=QUIT
```