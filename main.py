import argparse
from logging.config import dictConfig

import requests
from fabric import Connection
from flask import Flask, json, request

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})


app = Flask(__name__)


def execute_command(server, command):
    app.logger.info("going to execute command {0} on {1}".format(command, server))
    try:
        result = Connection(server).run(command, hide=True)
        if result.ok:
            app.logger.debug("executed {0} succesfully".format(command))
            return True, None
        else:
            app.logger.error("error executing {0}: {1}".format(command, result))
            return False, "o: {0}, e: {1}".format(result.stdout.strip(), result.stderr.strip())
    except Exception as e:
        app.logger.exeption("failure for {0} on {1}".format(command, server))
        return False, str(e)


def update_compose(server):
    for command in ['docker-compose down', 'docker-compose pull', 'docker-compose up -d']:
        r, m = execute_command(server, command)
        if not r:
            return False, m
    return True, None


def callback_url(payload):
    if not payload:
        app.logger.error("no payload for request")
        return None
    try:
        data = json.loads(payload)
        if not data:
            app.logger.error("no payload for request")
            return None
        if not 'callback_url' in data:
            app.logger.error("no callback url in data")
            return None
        return data['callback_url']
    except:
        app.logger.error("payload data not in JSON format")
        return None


def post_back(uri, data):
    r = requests.post(uri, data=data)
    if not r.status_code:
        app.logger.error("could not post {0} to {1} ({2}: {3})".format(data, uri, r.status_code, r.reason))
        return 'error on posting to endpoint', 500
    else:
        app.logger.debug("posted {0} to {1}".format(data, uri))
        return 'success', 200


@app.errorhandler(404)
def not_found_error(error):
    return '', 404


@app.route('/hooks/<variable>', methods=['GET', 'POST', 'PUT'])
def hooks(variable):
    uri = callback_url(request.data)
    if not uri:
        return post_back(uri, {'state': 'error', 'description': 'no valid callback given', 'context': 'whf'})
    stat, m = update_compose(variable)
    if stat:
        return post_back(uri, {'state': 'success', 'description': 'upgrade done', 'context': 'whf'})
    return post_back(uri, {'state': 'failure', 'description': m, 'context': 'whf'})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start our server in development mode.')
    parser.add_argument('-p', '--port', dest='port', default=5000, type=int, help='Port number for server')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()

    app.run(host='0.0.0.0', port=args.port, debug=args.debug)
