from bs4 import BeautifulSoup, SoupStrainer
import requests
import sys
import os

telmes = os.environ.get('telapi')
chat_id = os.environ.get('chatid')

def sendmes(message):
    payload = {'text': message}
    payload['chat_id'] = chat_id
    print(requests.post(telmes,data=payload))