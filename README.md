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
Clone this repository in `/usr/share/whf`, or modify the uwsgi.ini to reflect your location.
```bash
apt install python-virtualenv python3-pip uwsgi supervisor nginx
```

####Virtual environment
```bash
apt install 
cd /
mkdir venv
cd venv
virtualenv -p /usr/bin/python3 whf
source whf/bin/activate
pip3 install -r /usr/share/whf/requirements.txt
```
####NGINX
/etc/nginx/sites-available/app.conf
```bash
server {
    location / {
        include uwsgi_params;
        uwsgi_pass unix:///tmp/uwsgi.sock;
    }
}
```
```bash
ln -sf /etc/nginx/sites-available/app.conf /etc/nginx/sites-enabled/default
```

####uWSGI
/etc/uwsgi/uwsgi.ini
```ini
[uwsgi]
socket = /tmp/uwsgi.sock

master = true
processes = 2

chown-socket = nginx:nginx
chmod-socket = 664

hook-master-start = unix_signal:15 gracefully_kill_them_all

chdir = /usr/share/whf
module = main
callable = app
```

####Supervisord
/etc/supervisor/conf.d/app.conf
```ini
[program:whf]
user=ubuntu
virtualenv=/venv/whf
command=uwsgi --ini /etc/uwsgi/uwsgi.ini
priority=1
stopsignal=QUIT
stdout_logfile = /var/log/supervisor/whf-app.log
stdout_logfile_backups = 5
stderr_logfile = /var/log/supervisor/whf-app-error.log
stderr_logfile_backups = 5
```
