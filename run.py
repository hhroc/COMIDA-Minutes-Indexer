from flask import Flask
from flask import render_template
from flask import request

import json

import elasticsearch

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search.json', methods=['GET'])
def search():
    
    # decode the phrase being searched for
    try:
        phrase = request.args['phrase']
    except:
        phrase = ""

    # which page of the search results to display
    try:
        page = int(request.args['page'])
    except:
        page = 0

    # create our response
    response = {}
    response['success'] = False
    response['count'] = 0
    response['results'] = []
    
    # Make sure we are actually searching for something, and if so then
    # perform the search
    if not phrase == "":

        try:

            # perform the search
            results = es.search(index="comida",
                                body={
                                    "size": 10,
                                    "from": page*10,
                                    "query": {
                                        "match": {
                                            "pdftext": phrase
                               }}})

            # create our return object to send back
            response['success'] = True
            response['count'] = len(results['hits']['hits'])
            response['results'] = []
            for hit in results['hits']['hits']:
                response['results'].append({
                    'score': hit['_score'],
                    'docid': hit['_id'],
                    'docurl': hit['_source']['docurl'],
                    'scrapedatetime': hit['_source']['scrapedatetime'],
                    'linktext': hit['_source']['linktext'],
                    'targeturl': hit['_source']['targeturl']
                })

    except:
        pass

    # respond with the response serilized object
    return json.dumps(response)

if __name__ == "__main__":
    print "Web Application Starting ..."
    
    host = '0.0.0.0'
    port = 8080
    
    app.run(host=host, port=port)
