from evernote.api.client import EvernoteClient
from dotenv import load_dotenv
import os
load_dotenv()

client = EvernoteClient(
    consumer_key=os.getenv("EVERNOTE_KEY"),
    consumer_secret=os.getenv("EVERNOTE_SECRET"),
    sandbox=False # Default: True
)
request_token = client.get_request_token('http://localhost')
print(client.get_authorize_url(request_token))