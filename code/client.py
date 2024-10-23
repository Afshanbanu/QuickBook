from zeep import Client
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from pathlib import Path  # Python 3.6+ only
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
url=os.getenv("url")
username=os.getenv("username")
password=os.getenv("password")
print(username)
print(password)
hello_client = Client('http://127.0.0.1:8000/?wsdl')
resp=hello_client.service.authenticate("admin", "password")
print(resp)
ticket=resp[0]
print(hello_client.service.clientVersion(1.5))
print(hello_client.service.closeConnection(ticket))
print(hello_client.service.getLastError(ticket))

