from httpx import Client
from time import sleep


class captmonster(Client):
    def __init__(self, clientKey):
        super().__init__(
            headers={'content-type': 'application/json', 'accept': 'application/json'},
            base_url='https://api.capmonster.cloud',
            timeout=10
        )

        self.clientKey = clientKey
        self.status, self.response = self.verify()

    def verify(self):
        try:
            requests = self.post(
                url='/getBalance', 
                json={"clientKey": self.clientKey}
            )
        except: return False, 'CONNECTED HOST HAS FAILED TO RESPOND'

        if (requests.status_code in [200, 204]):
            return True, requests.json().get('balance')

        elif ('ERROR_KEY_DOES_NOT_EXIST' in requests.text):
            return False, 'ERROR KEY DOES NOT EXIST'

        elif ('ERROR_IP_BLOCKED' in requests.text):
            return False, 'ERROR IP BLOCKED'

        else: return False, requests.text

    def createTask(self, sitekey, useragent, rqdata=None):
        tasks = {
            "type"             :"HCaptchaTaskProxyless",
            "isInvisible"      : True,
            "websiteURL"       : "https://discord.com",
            "websiteKey"       : sitekey,
            "userAgent"        : useragent
        }

        if (rqdata != None):
            tasks['data'] = rqdata

        requests = self.post(
            url='/createTask', 
            json={'clientKey': self.clientKey, 'task': tasks}
        ).json()

        return requests['taskId']
    
    def getTaskResult(self, task_id):
        while True:
            try:
                print('(getTaskResult) with task id %s' % (task_id))
                requests = self.post(
                    url='/getTaskResult',
                    json={'clientKey': self.clientKey, 'taskId': task_id}
                ).json()

                if (requests['status'] == 'ready'):
                    return requests["solution"]["gRecaptchaResponse"]
                
                sleep(1)
            except: pass