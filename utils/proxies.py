from httpx import get
from random import choice


def verify(proxie):
    try:
        requests = get('https://api.ipify.org?format=json', proxies={
            "http://": "http://%s" % (proxie),
            "https://": "http://%s" % (proxie)
        }).json()

        return True, requests['ip']
    except Exception as error: 
        return False, error

def rotate(proxies: dict):
    while True:
        proxie = choice(proxies)
        status, data = verify(proxie)

        if (status == True):
            return proxie, data