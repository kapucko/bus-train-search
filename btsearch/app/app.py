import atexit
from datetime import datetime

from flask import Flask,render_template, request

from btsearch.searchers import RegioJetSearcher
from btsearch.config_loader import ConfigLoader

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config_loader = ConfigLoader('config.json')


@app.route("/search")
def search():
   return render_template('search_form.html', title=app.config_loader.config.get('title', 'Default'))

@app.route("/results")
def get_routes():
    print(request.args)
    searcher = RegioJetSearcher(app.config_loader.config)
    d = datetime.strptime(request.args.get('date'), '%Y-%m-%d')
    from_ = request.args.get('from')
    to = request.args.get('to')
    results = searcher.get_route(from_, to, d)

    return render_template('results.html', connections=results)
