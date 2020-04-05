import requests

from bs4 import BeautifulSoup

from helpers import CONSTANTS
from helpers.Crypto import Crypto
from helpers.RucaptchaAPI import RucaptchaAPI
from helpers.Utils import Utils


class API:
    def __init__(self, login, password, proxy, api_key):
        self.session = requests.Session()
        self.session.headers.update({
            'user-agent': CONSTANTS.USER_AGENT
        })

        self.captcha_key = api_key

        self.update_proxy(proxy)
        self.parse_token()
        self.auth(login, password)
        
    def parse_token(self):
        with self.session as s:
            self.csrf_token = s.get('https://freebitco.in/?op=signup_page').cookies.get('csrf_token')

    def parse_hash(self, token):
        with self.session as s:
            return s.get(f'https://freebitco.in/cgi-bin/fp_check.pl?s={token}&csrf_token={self.csrf_token}', headers={
                'x-csrf-token': self.csrf_token,
                'X-Requested-With': 'XMLHttpRequest'
            }).text

    def auth(self, login, password):
        with self.session as s:
            r = s.post('https://freebitco.in/', headers={
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'x-csrf-token': self.csrf_token,
                'x-requested-with': 'XMLHttpRequest'
            }, data={
                'csrf_token': self.csrf_token,
                'op': 'login_new',
                'btc_address': login,
                'password': password
            })

            try:
                for cookie in [requests.cookies.create_cookie(name, value, domain='freebitco.in', path='/') 
                               for name, value in [('btc_address', r.text.split(':')[1]),
                                                   ('password', r.text.split(':')[2]),
                                                   ('have_account', '1'),
                                                   ('cookieconsent_dismissed', 'yes'),
                                                   ('hide_push_msg', '1')]]:
                    self.session.cookies.set_cookie(cookie)
            except Exception:
                raise IndexError(f'{login}; {r.text}') # auth error         

    def create_data(self) -> dict:
        with self.session as s:
            r = s.get('https://freebitco.in')

            soup = BeautifulSoup(r.text, 'html.parser')

            token_key1 = Utils.match_text(r"token_name = '.*?'", r.text)[14:-1]
            token_val1 = Utils.match_text(r"var token1 = '.*?'", r.text)[14:-1]
            
            token_key2 = Utils.match_text(r"tcGiQefA = '.*?'", r.text)[12:-1]
            token_val2 = Crypto.create_token( self.parse_hash(token_key2) )

            data = {
                'csrf_token': self.csrf_token,
                'op': 'free_play',
                'fingerprint': Crypto.create_fingerprint(),
                'client_seed': soup.find(id='next_client_seed')['value'],
                'fingerprint2': Crypto.create_fingerprint2(),
                'pwc': soup.find(id='pwc_input')['value']
            }

            data[token_key1] = token_val1 
            data[token_key2] = token_val2
            data['g_recaptcha_response'] = RucaptchaAPI.solve_captcha(self.captcha_key) 

            return data

    def parse_coins(self):
        with self.session as s:
            r = s.get('https://freebitco.in/?op=home')

            return BeautifulSoup(r.text, 'html.parser').find(id='balance_small').text        

    def collect_coins(self, data) -> tuple:
        with self.session as s:
            r = s.post('https://freebitco.in/', headers={
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'x-csrf-token': self.csrf_token,
                'x-requested-with': 'XMLHttpRequest'
            }, data=data)

            result = r.text.split(':')

            if len(result) < 4:
                raise ValueError(f'{r.text}')
            
            return (result[2], result[3])

    def update_proxy(self, proxy):
        if not proxy == '-':
            self.session.proxies.update({
                proxy.split('://')[0]: proxy
            })