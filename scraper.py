import simplejson
import uuid
from time import strftime

import elasticsearch

# scraper from barkingowl lib
from BarkingOwl.scraper.scraper import Scraper

# download and unpdfer tools
from dler.dler import DLer
from unpdfer.unpdfer import UnPDFer

class Wrapper():

    def __init__(self):

        uid = str(uuid.uuid4())
        self.scraper = Scraper(uid=uid)

    def processDoc(self,payload):

        """
        {
            'sourceid': 'a0351229-3ebd-42b2-add7-4dea1012f96b', 
            'destinationid': 'broadcast', 
            'command': 'found_doc', 
            'message': {
                'scrapedatetime': '2014-02-03 22:47:25', 
                'docurl': u'http://www.growmonroe.org/files/file/Minutes/2014/MINUTES_2014_0121_Draft.pdf', 
                'urldata': {
                    'maxlinklevel': 1, 
                    'description': 'COMIDA Meeting Minutes Website', 
                    'title': 'COMIDA Minutes', 
                    'doctype': 'application/pdf', 
                    'targeturl': 'http://www.growmonroe.org/board-meetings', 
                    'creationdatetime': '2014-02-03 22:47:20'
                }, 
                'linktext': u'Minutes'
            }
        }
        """

        scrapedatetime = payload['message']['scrapedatetime']
        docurl = payload['message']['docurl']
        linktext = payload['message']['linktext']

        success,pdftext,pdfhash = self.getText(docurl)

        if success:
            
            # create instance of our elastic search api
            es = elasticsearch.Elasticsearch()

            # create the body we are going to send to elastic search
            body = {
                'scrapedatetime': scrapedatetime,
                'docurl': docurl,
                'linktext': linktext,
                'pdftext': pdftext,
                'pdfhash': pdfhash,
            }

            # make sure the doc doesn't already exist within the index
            if not self.checkexists(pdfhash):
                retval = True

                # index the doc
                es.index(
                    index="comida",
                    doc_type="pdfdoc",
                    id=uuid.uuid4(),
                    body=body,
                )

                print "Document Indexed."

            else:
                print "Skipping Document, Already Indexed."

        else:
            print "Error processing PDF document."

    def getText(self,url):

        # download the pdf
        dler = DLer()
        downloaddir = "./downloads"
        files,success = dler.dl([url],downloaddir)

        # check for success, and get filename
        if success:
            filename,dldatetime = files[0]
        else:
            print "Error downloading pdf document."

        # convert the pdf
        unpdfer = UnPDFer(filename)
        created,pdftext,pdfhash,success = unpdfer.unpdf(filename,SCRUB=True,verbose=False)

        return success,pdftext,pdfhash

    def checkexists(self,pdfhash):

        # handle misfit case
        if pdfhash == "":
            return False

        body = {
            "query": {
                "match": {
                    "pdfhash": pdfhash
                }
            }
        }
        try:
            results = self.es.search(index="comida",
                                     body=body
            )
        except:
            # if we get here, the index is probably empty
            return False
        exists = False
        if len(results['hits']['hits']) > 0:
            exists = True

        return exists


    def finishedCallback(self,payload):
        #print "Scraper Stpped ..."
        self.scraper.stop()

    def startedCallback(self,payload):
        #print "Scraper Started ..."
        pass

    def broadcastDocCallback(self,payload):
        #print "Document Found ..."

        #print payload

        self.processDoc(payload)

        #raise Exception('debug')

    def go(self):

        print "Creating Scraper ..."

        #uid = str(uuid.uuid4())   
        #scraper = Scraper(uid=uid)

        print "Setting up Scraper ..."

        self.scraper.setFinishedCallback(self.finishedCallback)
        self.scraper.setStartedCallback(self.startedCallback)
        self.scraper.setBroadcastDocCallback(self.broadcastDocCallback)

        urldata = {
            'targeturl': "http://www.growmonroe.org/board-meetings",
            'title': "COMIDA Minutes",
            'description': "COMIDA Meeting Minutes Website",
            'maxlinklevel': 1,
            'creationdatetime': str(strftime("%Y-%m-%d %H:%M:%S")),
            'doctype': 'application/pdf',
        }

        self.scraper.seturldata(urldata)

        print "Starting Scraper ..."

        self.scraper.start()
        self.scraper.begin()

if __name__ == "__main__":

    print "Starting ..."

    wrapper = Wrapper()

    wrapper.go()

    print "Done."
