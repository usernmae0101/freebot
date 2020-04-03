import requests as rq

from time import sleep

from helpers import CONSTANTS


class RucaptchaAPI:
    @classmethod
    def solve_captcha(cls, key, interval=10):
        r = rq.get('https://rucaptcha.com/in.php', params={
            'key': key,
            'json': '1',
            'method': 'userrecaptcha',
            'googlekey': CONSTANTS.CAPTHCA_KEY,
            'pageurl': CONSTANTS.CAPTCHA_DOMAIN
        })
        r.raise_for_status()
        
        id = r.json()['request']

        while True:
            sleep(interval)
            answer = cls.get_answer(key, id)
            if int(answer['status']) == 1:
                return answer['request']

    @staticmethod    
    def get_answer(key, id):
        r = rq.get('https://rucaptcha.com/res.php', params={
            'json': '1', 'key': key, 'action': 'get', 'id': id
        })
        r.raise_for_status()

        return r.json()