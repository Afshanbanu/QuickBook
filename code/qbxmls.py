from lxml import etree

def buildRequest(query,iteratorID=""):
    buildRequest.requestID=1
    number_of_documents_to_retrieve_in_each_iteration = 100
    attributes = {}
    if not iteratorID:
        attributes['iterator'] = "Start"
    else:
        attributes['iterator'] = "Continue"
        attributes['iteratorID'] = iteratorID
    attributes['requestID'] = str(buildRequest.requestID)
    root = etree.Element("QBXML")
    root.addprevious(etree.ProcessingInstruction("qbxml", "version=\"8.0\""))
    msg = etree.SubElement(root,'QBXMLMsgsRq', {'onError':'stopOnError'})
    irq = etree.SubElement(msg,query,attributes)
    mrt = etree.SubElement(irq,'MaxReturned')
    mrt.text= str(number_of_documents_to_retrieve_in_each_iteration)
    tree = etree.ElementTree(root)
    requestxml = etree.tostring(tree, xml_declaration=True, encoding='UTF-8')
    buildRequest.requestID += 1
    return requestxml
#'InvoiceQueryRq','CustomerQueryRq'


def request_b():
    queue=[]
    r1=buildRequest('InvoiceQueryRq')
    r2=buildRequest('CustomerQueryRq')
    queue=[r1,r2]
    return queue
re=request_b()
print(re)
