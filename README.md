# QuickbookPOC
Connect with quickBook desktop with Web Connector, get the data and generate report using Microsoft powerBI

#Guidance
The QBWC programmer's guide at https://static.developer.intuit.com/qbSDK-current/doc/pdf/QBWC_proguide.pdf.

The spyne Hello World example at http://spyne.io/docs/2.10/manual/02_helloworld.html.

A file .evn is needed and give username which is should be same as in pyQBWC.qwc and password which is should be give in the Quickbooks web connector.

#Run
#Run server.py file by the command
python server.py

#Run generate_qwc.py file by the command, which generate qb.qwc file which is to add in Quickbooks desktop web connector
python generate_qwc.py
