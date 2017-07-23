from datetime import datetime

from flask import Flask, jsonify, request

from btsearch.searchers import RegioJetSearcher
from btsearch.config_loader import ConfigLoader

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config_loader = ConfigLoader('config.json')


@app.route('/api/search', methods=['GET'])
def search():
    searcher = RegioJetSearcher(app.config_loader.config)
    d = datetime.strptime(request.args.get('date'), '%Y-%m-%d')
    from_ = request.args.get('from')
    to = request.args.get('to')
    results = searcher.get_route(from_, to, d)
    return jsonify(results)