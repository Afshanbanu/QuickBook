import json
import uuid
from spyne import Application, srpc, ServiceBase, Array, Integer, Unicode, Iterable, ComplexModel
from spyne.protocol.soap import Soap11
import time
# import db
from lxml import etree
from code import qbxmls
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
# from code.qbxml import buildRequest
import lxml as l
import xml.etree.ElementTree as et
import xmltodict
import pandas as pd
import json as js
import csv

requestQueue = {'job':'retrieve_customers'}


class qbwcSessionManager():
    def __init__(self, sessionQueue=[]):
        self.sessionQueue = sessionQueue  # this is a first in last out queue, i.e. a stack

    def check_requests(self):
        # checks the process requestQueue to see if there are any requests, if so, put them in sessionQueue
        while not requestQueue:
            req = requestQueue
            # interpret the msg fire off the correct function it will return a session to be put in the sessionqueue
            if req['job'] == 'retrieve_invoices':
                self.retrieve_invoices()
            elif req['job'] == 'retrieve_customers':
                self.retrieve_customers()
            else:
                return

    def queue_session(self, msg):
        # when called create a session ticket and stuff it in the store
        if 'ticket' not in msg or not msg['ticket']:
            ticket = str(uuid.uuid1())
        else:
            ticket = msg['ticket']
        if 'updatePauseSeconds' in msg:
            updatePauseSeconds = msg['updatePauseSeconds']
        else:
            updatePauseSeconds = 0
        if 'MinimumRunEveryNSeconds' in msg:
            MinimumRunEveryNSeconds = msg['MinimumRunEveryNSeconds']
        else:
            MinimumRunEveryNSeconds = 15
        if 'minimumUpdateSeconds' in msg:
            minimumUpdateSeconds = msg['minimumUpdateSeconds']
        else:
            minimumUpdateSeconds = 15
        self.sessionQueue.append({"ticket": ticket, "reqXML": msg['reqXML'], "callback": msg["callback"],
                                  "updatePauseSeconds": updatePauseSeconds,
                                  "minimumUpdateSeconds": minimumUpdateSeconds,
                                  "MinimumRunEveryNSeconds": MinimumRunEveryNSeconds})

    def get_session(self):
        self.check_requests()
        if self.sessionQueue:
            return self.sessionQueue[0]
        else:
            return ""

    def send_request(self, ticket):
        if self.sessionQueue:
            if ticket == self.sessionQueue[0]['ticket']:
                ret = self.sessionQueue[0]['reqXML']
                return ret
            else:
                print("tickets do not match. There is trouble somewhere")
                return ""

    def return_response(self, ticket, response):
        if ticket == self.sessionQueue[0]['ticket']:
            callback = self.sessionQueue[0]['callback']
            self.sessionQueue.pop(0)
            callback(ticket, response)
        else:
            return ""

    def iterate_invoices_start(self):
        request = qbxmls.invoice_request_iterative()
        session_manager.queue_session(
            {'reqXML': request, 'ticket': "", 'callback': self.iterate_invoices_continue, 'updatePauseSeconds': "",
             'minimumUpdateSeconds': 60, 'MinimumRunEveryNSeconds': 45})

    def iterate_invoices_continue(ticket, responseXML):
        # db.insert_invoice(responseXML)
        root = etree.fromstring(responseXML)
        # do something with the response, store it in a database, return it somewhere etc
        requestID = int(root.xpath('//InvoiceQueryRs/@requestID')[0])
        iteratorRemainingCount = int(root.xpath('//InvoiceQueryRs/@iteratorRemainingCount')[0])
        iteratorID = root.xpath('//InvoiceQueryRs/@iteratorID')[0]
        print("iteratorID", iteratorID, "iteratorRemainingCount:", iteratorRemainingCount, 'requestID', requestID)
        if iteratorRemainingCount:
            requestID += 1
            request = qbxmls.invoice_request_iterative(requestID=requestID, iteratorID=iteratorID)
            session_manager.queue_session(
                {'reqXML': request, 'ticket': ticket, 'callback': ticket.iterate_invoices_continue, 'updatePauseSeconds': "",
                 'minimumUpdateSeconds': 60, 'MinimumRunEveryNSeconds': 45})

    def iterate_customers_start(self):
        request = qbxmls.customer_request_iterative()
        session_manager.queue_session(
            {'reqXML': request, 'ticket': "", 'callback': self.iterate_customers_continue, 'updatePauseSeconds': "",
             'minimumUpdateSeconds': 60, 'MinimumRunEveryNSeconds': 45})

    def iterate_customers_continue(ticket, responseXML):
        # db.insert_customer(responseXML)
        root = etree.fromstring(responseXML)
        # do something with the response, store it in a database, return it somewhere etc
        requestID = int(root.xpath('//CustomerQueryRs/@requestID')[0])
        iteratorRemainingCount = int(root.xpath('//CustomerQueryRs/@iteratorRemainingCount')[0])
        iteratorID = root.xpath('//CustomerQueryRs/@iteratorID')[0]
        print("iteratorID", iteratorID, "iteratorRemainingCount:", iteratorRemainingCount, 'requestID', requestID)
        if iteratorRemainingCount:
            requestID += 1
            request = qbxmls.customer_request_iterative(requestID=requestID, iteratorID=iteratorID)
            session_manager.queue_session(
                {'reqXML': request, 'ticket': ticket, 'callback': ticket.iterate_customers_continue, 'updatePauseSeconds': "",
                 'minimumUpdateSeconds': 60, 'MinimumRunEveryNSeconds': 45})

    def retrieve_invoices(self):
        root = etree.Element("QBXML")
        root.addprevious(etree.ProcessingInstruction("qbxml", "version=\"8.0\""))
        msg = etree.SubElement(root, 'QBXMLMsgsRq', {'onError': 'stopOnError'})
        irq = etree.SubElement(msg, 'InvoiceQueryRq', {'requestID': '4'})
        mrt = etree.SubElement(irq, 'MaxReturned')
        mrt.text = "10"
        tree = etree.ElementTree(root)
        request = etree.tostring(tree, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        session_manager.queue_session({'reqXML': request, 'callback': self.invoice_return})

    def invoice_return(ticket, responseXML):
        with open('invoiceout', 'w') as invout:
            invout.write(responseXML)
        print("invoice saved in file")

    def retrieve_customers(self):
        root = etree.Element("QBXML")
        root.addprevious(etree.ProcessingInstruction("qbxml", "version=\"8.0\""))
        msg = etree.SubElement(root, 'QBXMLMsgsRq', {'onError': 'stopOnError'})
        irq = etree.SubElement(msg, 'CustomerQueryRq', {'requestID': '4'})
        mrt = etree.SubElement(irq, 'MaxReturned')
        mrt.text = "10"
        tree = etree.ElementTree(root)
        request = etree.tostring(tree, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        session_manager.queue_session({'reqXML': request, 'callback': self.customer_return})

    def customer_return(ticket, responseXML):
        with open('customerout', 'w') as invout:
            invout.write(responseXML)
        print("customer saved in file")


class QBWebService(ServiceBase):

    @srpc(Unicode, Unicode, _returns=Array(Unicode))
    def authenticate(strUserName, strPassword):
        print("authen")
        returnArray = []
        if strUserName == "admin" and strPassword == "password":
            print("inside authenticate")
            returnArray.append(str(uuid.uuid1()))
            '''session_manager=qbwcSessionManager()
            session = session_manager.get_session()
            print("session---",session)
            if 'ticket' in session:
                returnArray.append(session['ticket'])
                # returnArray.append(config['qwc']['qbwfilename']) # returning the filename indicates there is a request in the queue
                returnArray.append(str(session['updatePauseSeconds']))
                returnArray.append(str(session['minimumUpdateSeconds']))
                returnArray.append(str(session['MinimumRunEveryNSeconds']))
            else:
                returnArray.append("none")  # don't return a ticket if there are no requests
                returnArray.append("none")  # returning "none" indicates there are no requests at the moment'''
        else:
            #returnArray.append("no ticket")  # don't return a ticket if username password does not authenticate
            returnArray.append('nvu')
        print(returnArray)
        return returnArray

    @srpc(Unicode, _returns=Unicode)
    def clientVersion(strVersion):
        return ""

    @srpc(Unicode, _returns=Unicode)
    def closeConnection(ticket):
        return "OK"

    @srpc(Unicode, Unicode, Unicode, _returns=Unicode)
    def connectionError(ticket, hresult, message):
        return "done"

    @srpc(Unicode, _returns=Unicode)
    def getLastError(ticket):
        return "Error message here!"

    @srpc(Unicode, Unicode, Unicode, Unicode, Integer, Integer, _returns=Unicode)
    def sendRequestXML(ticket, strHCPResponse, strCompanyFileName, qbXMLCountry, qbXMLMajorVers, qbXMLMinorVers):
        reqXML = session_manager.send_request(ticket)
        return reqXML

    @srpc(Unicode, Unicode, Unicode, Unicode, _returns=Integer)
    def receiveResponseXML(ticket, response, hresult, message):
        print(response)
        session_manager.return_response(ticket, response)
        return 10

session_manager = qbwcSessionManager()
application = Application([QBWebService], 'http://developer.intuit.com/',
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11())

wsgi_application = WsgiApplication(application)



if __name__ == '__main__':
    import logging

    from wsgiref.simple_server import make_server

    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('spyne.protocol.xml').setLevel(logging.DEBUG)

    logging.info("listening to http://127.0.0.1:8000")
    logging.info("wsdl is at: http://127.0.0.1:8000/?wsdl")

    server = make_server('127.0.0.1', 8000, wsgi_application)
    server.serve_forever()




