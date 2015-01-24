import inspect
import os

from runipy.notebook_runner import NotebookRunner, NotebookError
from IPython.nbformat.current import read

from IPython.nbconvert.exporters.html import HTMLExporter

from flask import Flask
from flask import request

app = Flask(__name__)


def flask_notebook(fn):
    def wrapper():
        try:
            lines = inspect.getsourcelines(fn)
            src = ''.join(lines[0][2:])
            
            args = []
            for k, v in request.args.iteritems():
                # FIXME: only alpha_num in k
                # FIXME: escape? v
                args.append('{k}="{v}",'.format(k=k, v=v))
            call = '{fn}({args})'.format(
                fn=fn.__name__,
                args=', '.join(args)
            )

            src = src + '\n' + call

            return _run_code(src)
        except Exception as e:
            print e
            raise

    return wrapper


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
    exporter = HTMLExporter(template_file='custom', extra_loaders=[fsl])

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


@app.route('/p')
@flask_notebook
def p(x):
    print x


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8443)
