from flask import Flask
from flask import render_template
from flask import request

import json
import re
from time import strftime
from datetime import date, timedelta

from pymongo import MongoClient

import elasticsearch

app = Flask(__name__, static_folder='web/static', static_url_path='')
app.template_folder = "web"
app.debug = True

dbclient = MongoClient('mongodb://localhost:27017/')
db = dbclient['comidadb']
collection = db['comida']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stats')
def stats():
    return render_template('stats.html')

@app.route('/about')
def about():
    return render_template('about.html')

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
    if not phrase == "" and len(phrase) > 4:

        # save the phrase to the database
        savesearch(phrase)

        if True:
        #try:

            es = elasticsearch.Elasticsearch()

            # perform the search
            results = es.search(index="comida",
                                body={
                                    "size": 300,
                                    "from": 0,
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
                    'linktext': hit['_source']['linktext'].replace('\n',' ').replace('\r',''),
                    'previewtext': buildpreviewtext(phrase,hit['_source']['pdftext']),
                    #'searchid': str(searchid),
                })

        #except:
        #    pass

        response['phrase'] = phrase

    # respond with the response serilized object
    return json.dumps(response)

@app.route('/searches.json', methods=['GET'])
def searches():

    searches = []
    for search in collection.find():
        searches.append({'phrase':search['phrase'],'count':search['count']})

    return json.dumps(searches)

def savesearch(phrase):

    today = str(date.today().strftime("%Y-%m-%d"))
    yesterday = str((date.today() - timedelta(1)).strftime("%Y-%m-%d"))
    result = collection.find_one({'phrase':phrase,
                                  '$or': [
                                      {'date':today}, 
                                      {'date':yesterday},
                                  ],
                                 })
    if result == None:
        print "Adding '{0}' to database.".format(phrase)
        search = {
            'phrase': phrase,
            'count': 1,
            'date': str(strftime("%Y-%m-%d")),
        }
        collection.insert(search)
    else:
        print "Increasing count by one for '{0}'".format(phrase)
        search = {
            'phrase': phrase,
            'count': result['count']+1,
        }
        collection.update({'_id':result['_id']},{'$set': search})

#
# Borrowed from MonroeMinutes 
#
def buildpreviewtext(phrase,pdftext):

    BEFORE_LEN = 64
    AFTER_LEN = 64

    regexstr = "( +)?"
    for i in range(0,len(phrase)):
        if phrase[i] != ' ':
            regexstr += "%s( +)?" % phrase[i]

    count = 0
    indexes = [(m.start(0)) for m in re.finditer(regexstr.lower(), pdftext.lower())]

    #print "Found %i incidents of phrase" % len(indexes)

    if len(indexes) == 0:
        return ""

    #print "pdftext length: {0}".format(len(pdftext))

    text = ""
    for index in indexes:
        #print "index = %i" % index
        if index < BEFORE_LEN:
            beforeindex = 0
        else:
            beforeindex = index - BEFORE_LEN
        #print "before index: {0}, len: {1}".format(beforeindex,AFTER_LEN)
        preview = pdftext[beforeindex:(beforeindex+BEFORE_LEN+AFTER_LEN)]
        preview = " ".join(preview.split(' ')[1:-1])
        preview = preview.replace('\t','').replace('\n','').replace('\f','')
        #print "preview text: {0}".format(preview)

        text += "... {0} ...".format(preview)

    return text


if __name__ == "__main__":
    print "Web Application Starting ..."
    
    host = '0.0.0.0'
    port = 8083
    
    fa = app.run(host=host, port=port)
