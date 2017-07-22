from datetime import datetime

from flask import Flask, jsonify, request

from btsearch.searchers import RegioJetSearcher

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True


@app.route('/search', methods=['GET'])
def search():
    searcher = RegioJetSearcher()
    d = datetime.strptime(request.args.get('date'), '%Y-%m-%d')
    from_ = request.args.get('from')
    to = request.args.get('to')
    results = searcher.get_route(from_, to, d)
    return jsonify(results)