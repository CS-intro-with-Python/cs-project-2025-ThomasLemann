import requests
import sys

responseone = requests.get('http://127.0.0.1:8080/')

if responseone.status_code != 200:
    sys.exit(1)
else:
    print(responseone.text)