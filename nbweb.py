import inspect
import re

from runipy.notebook_runner import NotebookRunner, NotebookError
from IPython.nbformat.current import read

from IPython.nbconvert.exporters.html import HTMLExporter

from flask import Flask
from flask import request

app = Flask(__name__)


def assert_valid_key_value(k, v):
    if not re.match("[_A-Za-z][_a-zA-Z0-9]*$", k):
        raise ValueError(
            '{k} is not a valid argument name'.format(k=k)
        )
                
    # not easy to escape perfectly... do this for now
    if '"""' in v:
        raise ValueError(
            'cant use """ quotes in the value.  sorry'
        )
        
    return True


def extract_def_src(fn):
    lines = inspect.getsourcelines(fn)
    for i, line in enumerate(lines[0]):
        if line.strip()[:4] == 'def ':
            break

    return ''.join(lines[0][i:])


def flask_notebook(fn):
    def wrapper():
        try:
            # FIXME: look for first line starting with def or
            # something like that
            src = extract_def_src(fn)
            
            args = []
            for k, v in request.args.iteritems():
                assert_valid_key_value(k, v)
                args.append('{k}="""{v}""",'.format(k=k, v=v))
            
            call = '{fn}({args})'.format(
                fn=fn.__name__,
                args=', '.join(args)
            )

            src = src + '\n' + call

            return _run_code(src)
        except Exception as e:
            print e
            raise

    # otherwise flask complains that there are multiple functions with
    # the name 'wrapper'
    import random
    wrapper.__name__ = 'wrapper' + str(random.random())

    return app.route('/' + fn.__name__)(wrapper)


def _run_code(code):
    """ code is a string """
    
    notebook_filename = '/home/ubuntu/notebook.ipynb'
    notebook_as_json_stream = open(notebook_filename)
    
    nb = read(notebook_as_json_stream, 'json')

    nb['worksheets'][0]['cells'][0]['input'] = code

    nb_runner = NotebookRunner(nb, True, True, '/tmp')

    try:
        nb_runner.run_notebook(skip_exceptions=True)
    except NotebookError:
        print "FIXME"

    from jinja2 import FileSystemLoader
    fsl = FileSystemLoader('/home/ubuntu/runipy')
    exporter = HTMLExporter(template_file='custom-basic', extra_loaders=[fsl])

    output, _ = exporter.from_notebook_node(nb_runner.nb)
    
    return output


def _run_notebook(notebook_as_json_stream, skip_exceptions=True):
    nb = read(notebook_as_json_stream, 'json')

    nb['worksheets'][0]['cells'][0]['input'] = "print 1\n"

    nb_runner = NotebookRunner(nb, True, True, '/tmp')

    try:
        nb_runner.run_notebook(skip_exceptions=skip_exceptions)
    except NotebookError:
        print "FIXME"

    exporter = HTMLExporter()

    output, _ = exporter.from_notebook_node(nb_runner.nb)
    
    return output


@flask_notebook
def p(x):
    x = int(x)
    plot([x, x**2, x**3, x**4])

@flask_notebook
def error(x=None):
    1/0


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8443)
