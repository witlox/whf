import argparse

from fabric import Connection
from flask import Flask

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


@app.route("/")
def root():
    return '', 404


@app.route("/backend/test/signal")
def test_backend():
    stat, m = update_compose('test')
    if stat:
        return 'success', 200
    return m, 500


@app.route("/backend/acceptance/signal")
def acceptance_backend():
    stat, m = update_compose('acc-be')
    if stat:
        return 'success', 200
    return m, 500


@app.route("/frontend/test/signal")
def test_frontend():
    stat, m = update_compose('test')
    if stat:
        return 'success', 200
    return m, 500


@app.route("/frontend/acceptance/signal")
def acceptance_frontend():
    stat, m = update_compose('acc-fe')
    if stat:
        return 'success', 200
    return m, 500


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start our server in development mode.')
    parser.add_argument('-p', '--port', dest='port', default=5000, type=int, help='Port number for server')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()

    app.run(host='0.0.0.0', port=args.port, debug=args.debug)
