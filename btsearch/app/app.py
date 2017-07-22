from datetime import datetime

from flask import Flask,render_template, request

from btsearch.searchers import RegioJetSearcher

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

@app.route("/search")
def search():
   return render_template('search_form.html', my_string='Hello world')

@app.route("/results")
def get_routes():
    print(request.args)
    searcher = RegioJetSearcher()
    d = datetime.strptime(request.args.get('date'), '%Y-%m-%d')
    from_ = request.args.get('from')
    to = request.args.get('to')
    results = searcher.get_route(from_, to, d)

    return render_template('results.html', connections=results)
