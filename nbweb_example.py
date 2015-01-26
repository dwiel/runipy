from flask import Flask
import nbweb

app = Flask(__name__)


@nbweb.flask_notebook(app)
def p(x):
    x = int(x)
    plot([x, x**2, x**3, x**4])


@nbweb.flask_notebook(app)
def error():
    1 / 0


@nbweb.flask_notebook(app)
def one():
    return 1


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8443)
