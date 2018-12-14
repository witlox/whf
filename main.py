from fabric import Connection
from flask import Flask

app = Flask(__name__)


def execute_command(server, command):
    try:
        result = Connection(server).run(server, command, hide=True)
        if result.ok:
            return True, None
        else:
            return False, "o: {0}, e: {1}".format(result.stdout.strip(), result.stderr.strip())
    except Exception as e:
        return False, e


def update_compose(server):
    for command in ['docker-compose down',
                    'docker-compose pull',
                    'docker-compose up']:
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
    app.run(host='0.0.0.0')
