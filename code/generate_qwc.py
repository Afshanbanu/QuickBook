from zeep import Client
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

url=os.getenv("url")
username=os.getenv("username")
password=os.getenv("password")
hello_client = Client(url)
resp=hello_client.service.authenticate(username, password)
print(resp)
qwc="""<?xml version="1.0"?>
<QBWCXML>
	<AppName>QuickBooks_webConnector</AppName>
	<AppID></AppID>
	<AppURL>http://localhost:8000/?wsdl</AppURL>
	<AppDescription></AppDescription>
	<AppSupport>http://localhost:8000</AppSupport>
	<UserName>admin</UserName>
	<OwnerID>{"""+resp[0]+"""}</OwnerID>
	<FileID>{57F3B9B6-86F1-4FCC-B1FF-967DE1813D20}</FileID>
	<QBType>QBFS</QBType>
	<Scheduler>
		<RunEveryNMinutes>2</RunEveryNMinutes>
	</Scheduler>
	<IsReadOnly>false</IsReadOnly>
</QBWCXML>"""
print(qwc)
os.chdir('../')
filepath=os.getcwd()+"\data"
print(filepath)
with open(filepath+"\qb.qwc","w") as file:
    file.write(qwc)
    file.close()


