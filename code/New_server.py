from spyne.protocol.soap import Soap11
from spyne import Application, rpc, ServiceBase, Iterable, Integer, Unicode
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.service import ServiceBase
from spyne.model.primitive import Integer, Unicode
from spyne.model.complex import Iterable, ComplexModel, Array
from spyne.decorator import srpc
from spyne.protocol.soap import Soap11
import uuid
import time
from requests import Session
from code.qbxml import buildRequest
from code.qbxmls import request_b
import lxml as l
import xml.etree.ElementTree as et
import xmltodict
import pandas as pd
import json as js
import csv
from pathlib import PurePath
import os
from xmlutils import xml2csv
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

url=os.getenv("url")
username=os.getenv("username")
password=os.getenv("password")
ip=os.getenv("ip")
port=os.getenv("port")

retval=0
count=-1
class QBWebService(ServiceBase):

    @srpc(Unicode, Unicode, _returns= Array(Unicode))
    def authenticate(strUserName, strPassword):
        returnArray = []
        returnArray.append(str(uuid.uuid1()))
        if strUserName == "admin" and strPassword == "password":
            returnArray.append("")
        else:
            returnArray.append("nvu")
            print(returnArray)
        return returnArray

    @srpc(Unicode, _returns=Unicode)
    def clientVersion(strVersion):
        '''recommendedVersion = 1.5
        supportedMinVersion = 1.0
        logging.debug('clientVersion %s', strVersion)
        if strVersion<recommendedVersion:
            retval="W:We recommend that you upgrade your QBWebConnector"
        elif strVersion<supportedMinVersion:
            retval="E:You need to upgrade your QBWebConnector"'''

        return ""

    @srpc(Unicode, _returns=Unicode)
    def closeConnection(ticket):
        session.close()
        logging.debug('closeConnection %s', ticket)
        return "OK"

    @srpc(Unicode, Unicode, Unicode, _returns=Unicode)
    def connectionError(ticket, hresult, message):
        logging.debug('connectionError %s %s %s', ticket, hresult, message)
        return "done"

    @srpc(Unicode, _returns=Unicode)
    def getLastError(ticket):
        global retval
        logging.debug('lasterror %s', ticket)
        if retval==-101:
            return "QuickBooks was not running!"
        else:
            # return "Error message here!"
            return "NoOp"

    @srpc(Unicode, Unicode, Unicode, Unicode, _returns=Integer)
    def receiveResponseXML(ticket, response, hresult, message):
        global count
        logging.debug('receiveResponseXML %s %s %s', ticket, hresult, message)

        if str(hresult) != "":
            retval = -101
        else:
            root = l.etree.fromstring(str(response))
            #print(response)
            re = xmltodict.parse(response)
            QBXML = re['QBXML']
            QBXMLMsgsRs = QBXML['QBXMLMsgsRs']
            for QueryRs_key in QBXMLMsgsRs.keys():
                QueryRs=QBXMLMsgsRs[QueryRs_key]
                for Ret_key in QueryRs.keys():
                    Ret=QueryRs[Ret_key]
            json_data = js.dumps(Ret)
            os.chdir('../')
            filepath = os.getcwd() + "\data"
            print(filepath)
            with open(filepath+"\QB_webConectorData.json", 'w') as json_file:
                json_file.write(json_data)
                json_file.close()
            json_file = pd.read_json(filepath + "\QB_webConectorData.json")
            csv_data = json_file.to_csv(filepath + "\\"+QueryRs_key+".csv", sep=',')
            time.sleep(5)
            req = request_b()
            if (count == (len(req)-1)):
                retval=100
            else:
                retval = 80
        return retval

    @srpc(Unicode, Unicode, Unicode, Unicode, Integer, Integer, _returns=Unicode)
    def sendRequestXML(ticket, strHCPResponse, strCompanyFileName, qbXMLCountry, qbXMLMajorVers, qbXMLMinorVers):
        global count
        #reqXML = session.get_reqXML(ticket)
        logging.debug('sendRequestXML')
        #logging.log(DEBUG2, 'sendRequestXML reqXML %s ', reqXML)
        #logging.log(DEBUG2, 'sendRequestXML strHCPResponse %s ', strHCPResponse)
        reqxml=request_b()
        count+=1
        return reqxml[count]


application = Application([QBWebService], 'http://developer.intuit.com/',
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11())

wsgi_application = WsgiApplication(application)


if __name__ == '__main__':
    import logging

    from wsgiref.simple_server import make_server

    session = Session()
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('spyne.protocol.xml').setLevel(logging.DEBUG)

    logging.info("listening to "+url)
    logging.info("wsdl is at: "+url)

    server = make_server(ip, int(port), wsgi_application)
    server.serve_forever()
