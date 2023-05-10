from utils.captcha import captmonster
from utils.scrape import DiscordSocket
from utils.proxies import rotate
from utils.config import tokens_main, guild_id, channel_id, tokens_path, message, captmonster_key, proxies_enable, proxies, JA3_fingerprint

from tls_client import Session
from itertools import cycle
from threading import Thread
from httpx import get
from time import sleep, time
from math import floor
from colorama import init, Fore
from random import randint, choice


def fetch_nonce():
    return str((floor(time() * 1000) - 1420070400000) * 4194304)

def fetch_cookies(client):
    try:
        return client.get('https://discord.com').cookies
    except: return ""


def fetch_fingerprint(client):
    try:
        request = client.get(f'https://discord.com/api/v9/experiments').json()
        return request['fingerprint']
    except: return ''

headers = {
    "accept": "*/*",
    "accept-language": "th-TH,th;q=0.9",
    "content-type": "application/json",
    "sec-ch-ua": "\"Chromium\";v=\"112\", \"Google Chrome\";v=\"112\", \"Not:A-Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-debug-options": "bugReporterEnabled",
    "x-discord-locale": "th",
    "origin": "https://discord.com",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6InRoLVRIIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzExMi4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTEyLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6Imh0dHBzOi8vZGlzY29yZC5jb20vIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiZGlzY29yZC5jb20iLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoxOTQyOTYsImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGwsImRlc2lnbl9pZCI6MH0=",
    "TE": "trailers"
}

def verify(tokens):
    return get('https://discord.com/api/v9/users/@me/library', headers={'authorization': tokens}).status_code

def server(tokens):
    return get('https://discord.com/api/v9/guilds/%s' % (guild_id), headers={'authorization': tokens}).status_code

def execute(client, method, url, payloads=None):
    def change_proxies():
        if (client.proxies != {}):
            proxie, _ = rotate(proxies)
            client.proxies = {"http": "http://%s" % (proxie)}

    while True:
        try:
            return method(url, json=payloads)
        except: change_proxies()

def accept_agreement(client):
    return execute(client, client.patch, 'https://discord.com/api/v7/users/@me/agreements', {"terms": True, "privacy": True}).text

def create(client, user_id):
    client.headers['x-context-properties'] = "e30="
    client.headers['referer'] = "https://discord.com/channels/%s/%s" % (guild_id, channel_id)

    return execute(client, client.post, 'https://discord.com/api/v7/users/@me/channels', {"recipients": [user_id]}).json()

def typing(client, channel_id):
    client.headers["referer"] = "https://discord.com/channels/@me/%s" % (channel_id)

    return execute(client, client.post, 'https://discord.com/api/v7/channels/%s/typing' % (channel_id))

def send(client, user_id, channel_id, message):
    try:
        del client.headers['x-context-properties']
    except: pass

    def request(captcha_key=None, captcha_rqtoken=None):
        payloads = {
            "content": message.replace('<user>', '<@%s>' % (user_id)),
            "flags": 0,
            "nonce": fetch_nonce(),
            "tts": False
        }

        if (captcha_key != None):
            payloads['captcha_key'] = captcha_key
            payloads['captcha_rqtoken'] = captcha_rqtoken

        # print(channel_id, client.headers['authorization'])

        return execute(client, client.post, 'https://discord.com/api/v9/channels/%s/messages' % (channel_id), payloads)
    
    while True:
        requests = request()

        while True:
            if (requests.status_code in [200, 204]):
                return True, requests.json()

            elif ("captcha_sitekey" in requests.text):

                objects = captmonster(captmonster_key)
                if (objects.status == False):
                    return False, objects.response
                
                else:
                    print('(Captcha) captcha require try to solve')
                    requests_ = requests.json()

                    taskId = objects.createTask(
                        sitekey=requests_['captcha_sitekey'],
                        useragent=client.headers['user-agent'],
                        rqdata=None if ('captcha_rqdata' not in requests_) else requests_['captcha_rqdata']
                    )

                    solution = objects.getTaskResult(taskId)

                    print('(Solve) captcha %s' % (solution[0:20]))
                    requests =  request(
                        captcha_key=solution,
                        captcha_rqtoken=requests_['captcha_rqtoken']
                    )
            else: break
        
        for alert in ['You need to verify your account', 'Cannot send messages to this user', 'You are opening direct messages too fast', 'Missing Access', '401: Unauthorized']:
            if (alert in requests.text):
                return False, alert
        
        if ('You are being rate limited.' in requests.text):
            data = requests.json()['retry_after']

            print('(Ratelimited): %s (sleep 15 sec)' % (
                str(data['retry_after']))
            )

            sleep(data['retry_after'])
        else:
            print('(Problem): %s sleep 5 second' % (requests.text))
            sleep(5)

def gate(user_id, tokens):
    if (len(JA3_fingerprint) == 0):
        ja3_string = "771,4866-4867-4865-49196-49200-49195-49199-52393-52392-159-158-52394-49327-49325-49326-49324-49188-49192-49187-49191-49162-49172-49161-49171-49315-49311-49314-49310-107-103-57-51-157-156-49313-49309-49312-49308-61-60-53-47-255,0-11-10-35-16-22-23-49-13-43-45-51-21,29-23-30-25-24,0-1-2"
    else: ja3_string = choice(JA3_fingerprint)

    client = Session(
        ja3_string=ja3_string,
        h2_settings={"HEADER_TABLE_SIZE": 65536, "MAX_CONCURRENT_STREAMS": 1000, "INITIAL_WINDOW_SIZE": 6291456, "MAX_HEADER_LIST_SIZE": 262144},
        h2_settings_order=[ "HEADER_TABLE_SIZE", "MAX_CONCURRENT_STREAMS", "INITIAL_WINDOW_SIZE", "MAX_HEADER_LIST_SIZE"],
        supported_signature_algorithms=["ECDSAWithP256AndSHA256", "PSSWithSHA256", "PKCS1WithSHA256", "ECDSAWithP384AndSHA384", "PSSWithSHA384", "PKCS1WithSHA384", "PSSWithSHA512", "PKCS1WithSHA512",],
        supported_versions=["GREASE", "1.3", "1.2"],
        key_share_curves=["GREASE", "X25519"],
        cert_compression_algo="brotli",
        connection_flow=15663105,

        client_identifier='chrome_112'
    )

    if (proxies_enable):
        proxy, ip = rotate(proxies)
        client.proxies = {"http": "http://%s" % (proxy)}
        print('(Proxies): %s - %s)' % (proxy, ip))

    while True:
        fingerprint = fetch_fingerprint(client=client)
        if (fingerprint == ''):
            print('(Problem): fetching fingerprint failed (try again in 5 sec)')
            sleep(5)
        else: break
    
    client.headers = headers
    client.headers['fingerprint'] = fingerprint

    fetch_cookies(client=client)

    client.headers['authorization'] = tokens

    accept_agreement(client=client)
    response = create(client, user_id)

    if ('id' in response):
        typing(client, response['id'])
        sleep(randint(1,3))

        status, requests = send(client, user_id, response['id'], message=message)

        if (status == True):
            print('%s(%s): %s%s' % (Fore.LIGHTGREEN_EX, str(user_id), message, Fore.RESET))
        else: print('(%s): %s' % (str(user_id), requests))
    else: print('(Problem): create direct channel - %s' % (response))

def prepare():
    init()

    tokens = []
    temp = []

    def verify_(token):
        if (verify(token) in [200, 204]):
            if (server(token) in [200, 204]):
                tokens.append(token)
                print(token[:-25], 'VALID')

            else: print(token[:-25], 'NOT IN SERVER')
        else: print(token[:-25], 'NEED VERIFY or UNAUTH')

    for token in open(tokens_path, 'r', encoding='utf-8').readlines():
        if (':' in token):
            token = token.split(':')[2]
        token = token.strip()
        
        thread = Thread(target=verify_, args=(token,))
        temp.append(thread)
        thread.start()

    for thread in temp:
        thread.join()

    return tokens


if (__name__ == '__main__'):
    objects = DiscordSocket(
        token=tokens_main, 
        guild_id=guild_id, 
        channel_id=channel_id,
        rbs=False
    )

    tokens = cycle(prepare())

    for member in objects.scrape():
        if (proxies_enable):
            Thread(target=gate, args=(member, next(tokens),)).start()
            sleep(0.1)
        
        else: gate(member, next(tokens))