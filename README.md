# Web Hook Forwarder
The idea is to run local commands on internal servers using SSH if you have external webhooks triggering it.
The implementation currently runs the docker compose chain for updating existing images.
This stupid simple setup assumes a server is configured in your ssh_config and can be called from http://<server_url>/hooks/<server_to_call>.

## Configure
Create a ssh config file in /etc/ssh/ssh_config and add entries for the servers you want to be able to call. 
Make sure the key used to connect to the servers is readable by the uWSGI uid (in this case: www-data)

```bash
Host <hostname should match entries above>
    HostName <ip address of internal development machine>
    User <user that can execute docker-compose>
    IdentityFile <path to the private key file for the specified user>
```

## Install
Clone this repository in `/usr/share/whf`, or modify the uwsgi.ini to reflect your location.
```bash
apt install python-virtualenv python3-pip uwsgi-plugin-python3 supervisor nginx
```

### Virtual environment
```bash
cd /
mkdir venv
cd venv
virtualenv -p /usr/bin/python3 whf
source whf/bin/activate
pip3 install -r /usr/share/whf/requirements.txt
```
### NGINX
/etc/nginx/sites-available/app.conf
```bash
server {
    location / {
        include uwsgi_params;
        uwsgi_pass unix:///var/run/uwsgi.sock;
    }
}
```
```bash
ln -sf /etc/nginx/sites-available/app.conf /etc/nginx/sites-enabled/default
```

### uWSGI
/etc/uwsgi/uwsgi.ini
```ini
[uwsgi]
socket = /var/run/uwsgi.sock

plugins = python3

uid = www-data
gid = www-data

master = true
processes = 2

chown-socket = www-data:www-data
chmod-socket = 664

hook-master-start = unix_signal:15 gracefully_kill_them_all

chdir = /usr/share/whf
module = main
callable = app
```

### supervisord
/etc/supervisor/conf.d/app.conf
```ini
[program:whf]
command=/venv/whf/bin/uwsgi --ini /etc/uwsgi/uwsgi.ini
priority=1
stopsignal=QUIT
stdout_logfile = /var/log/supervisor/whf-app.log
stdout_logfile_backups = 5
stderr_logfile = /var/log/supervisor/whf-error.log
stderr_logfile_backups = 5
```

Restart supervisor and nginx, and you're good to go.
