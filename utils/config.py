from json import loads


config = loads(open('config.json', 'r', encoding='utf-8').read())
captmonster_key = config['captmonster_key']

guild_id = config['guild_id']
channel_id = config['channel_id']

tokens = config['tokens']
tokens_main = tokens['main']
tokens_path = tokens['path']

proxies = config['proxies']
proxies_enable = proxies['enable']
proxies_path = proxies['path']

message = config['message']

JA3_fingerprint = [JA3.strip() for JA3 in open('./utils/JA3_fingerprint.txt', 'r', encoding='utf-8').readlines()]
if (proxies_enable == True):
    proxies = [proxy.strip() for proxy in open(proxies_path, 'r', encoding='utf-8').readlines()]