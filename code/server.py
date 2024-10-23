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
from requests import Session
from code.qbxml import buildRequest
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
        logging.debug('receiveResponseXML %s %s %s', ticket, hresult, message)

        if str(hresult) != "":
            retval = -101
        else:
            root = l.etree.fromstring(str(response))
            print(response)
            re = xmltodict.parse(response)
            QBXML=re['QBXML']
            QBXMLMsgsRs=QBXML['QBXMLMsgsRs']
            AccountQueryRs=QBXMLMsgsRs['AccountQueryRs']
            AccountRet=AccountQueryRs['AccountRet']
            print("re----")
            print(AccountRet)
            json_data=js.dumps(AccountRet)
            os.chdir('../')
            filepath = os.getcwd() + "\data"
            print(filepath)
            with open(filepath + "\QB_webConectorData.json",'w') as json_file:
                json_file.write(json_data)
                json_file.close()
            json_file = pd.read_json(filepath + "\QB_webConectorData.json")
            csv_data = json_file.to_csv(filepath + "\All_Account_csv.csv", sep=',')
            revenue=[]
            expense=[]
            cogs=[]
            csv_file = open(filepath + "\All_Account_csv.csv")
            reader = csv.reader(csv_file, delimiter=',')
            row_no=0
            for row in reader:
                if row_no==0:
                    expense.append(row)
                    revenue.append(row)
                    cogs.append(row)
                if row[9] == "Expense" or row[9]=="Equity" or row[9]=="AccountsPayable" or row[9]=="CreditCard" or row[9]=="OtherCurrentLiability" or row[9]=="LongTermLiability" or row[9]=="OtherExpense":
                    expense.append(row)
                if row[9] == "Bank" or row[9]=="Income" or row[9]=="OtherIncome" or row[9]=="AccountsReceivable" or row[9]=="OtherCurrentAsset" or row[9]=="FixedAsset":
                    revenue.append(row)
                if row[9] == "CostOfGoodsSold":
                    cogs.append(row)
                row_no+=1
            print(expense)
            print(revenue)
            print(cogs)
            r= open(filepath + "\Revenue.csv", 'w+',newline="")
            writer = csv.writer(r)
            writer.writerows(revenue)
            e=open(filepath + "\expense.csv",'w+',newline="")
            writer = csv.writer(e)
            writer.writerows(expense)
            c=open(filepath + "\cogs.csv",'w+',newline="")
            writer = csv.writer(c)
            writer.writerows(cogs)
            CustomerQueryRs = QBXMLMsgsRs['CustomerQueryRs']
            '''isIterator = root.xpath('boolean(//@iteratorID)')
            req = buildRequest()'''
            '''list_req = req.split("<?qbxml")
            print(len(list_req))
            total = len(list_req)-1
            print("total",total)
            count = session.size
            print(count)
            percentage = (count * 100) / total
            print("persen",percentage)
            if (percentage >= 100):
                count = 0
                session.size = 0'''
            retval = 100  # 100 percent done

        return retval

    @srpc(Unicode, Unicode, Unicode, Unicode, Integer, Integer, _returns=Unicode)
    def sendRequestXML(ticket, strHCPResponse, strCompanyFileName, qbXMLCountry, qbXMLMajorVers, qbXMLMinorVers):
        #reqXML = session.get_reqXML(ticket)
        logging.debug('sendRequestXML')
        #logging.log(DEBUG2, 'sendRequestXML reqXML %s ', reqXML)
        #logging.log(DEBUG2, 'sendRequestXML strHCPResponse %s ', strHCPResponse)
        reqxml=buildRequest()
        return reqxml


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
