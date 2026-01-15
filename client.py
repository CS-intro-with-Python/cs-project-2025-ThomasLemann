import requests
import sys

OK, ERR, RST = "\033[32m", "\033[31m", "\033[0m"

responseone = requests.get('http://127.0.0.1:8080/')

if responseone.status_code != 200:
    print(f"{ERR}Error occured{RST}")
    print(responseone.text)
else:
    print(f"{OK} Server is working correctly{RST}")
    print("::notice title=Healthcheck passed::Response is adequate")
    print(responseone.text)

responsetwo = requests.get('http://127.0.0.1:8080/login')

if responsetwo.status_code != 200:
    print(f"{ERR}Error occured{RST}")
    print(responsetwo.text)
else:
    print(f"{OK} Server is working correctly{RST}")
    print("::notice title=Healthcheck passed::Response is adequate")
    print(responsetwo.text)

responsethree = requests.get('http://127.0.0.1:8080/note')

if responsethree.status_code != 200:
    print(f"{ERR}Error occured{RST}")
    print(responsethree.text)
else:
    print(f"{OK} Server is working correctly{RST}")
    print("::notice title=Healthcheck passed::Response is adequate")
    print(responsethree.text)