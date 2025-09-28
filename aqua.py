import json
import os
import time
import math
import random
import secrets
import requests
import tls_client
import subprocess
import functools

from datetime import datetime
from tempmail_api import TempMailAPI
from concurrent.futures import ThreadPoolExecutor

if os.name == 'nt':
    import ctypes
    
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE = -11
    mode = ctypes.c_ulong()
    kernel32.GetConsoleMode(handle, ctypes.byref(mode))
    kernel32.SetConsoleMode(handle, mode.value | 0x0004)

R = '\033[31m'  # Red
C = '\033[36m'  # Cyan
L = '\033[90m'  # Grey
G = '\033[32m'  # Green
W  = '\033[0m'   # White
Y = '\033[33m'  # Yellow
B = '\33[94m'   # Blue
P = '\033[35m'  # Purple

API_KEY = "CAP-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
proxies = open('proxies.txt', 'r').read().strip().splitlines()

class Console:
    def log(content, color='G', mode='INF', space=5):
        _time = datetime.now().strftime('%H:%M:%S')

        print(f'{L}[{W}{_time}{L}] {color}{mode.upper()}{W}{" " * space}', content, W)

    def normal(content):
        _time = datetime.now().strftime('%H:%M:%S')

        print(f'{L}[{W}{_time}{L}]{W}', content, W)


class Reverse:
    def random_uint32():
        return math.floor(random.random() * 4294967296)

    def to_string(n):
        chars = '0123456789abcdefghijklmnopqrstuvwxyz'
        result = ''
        while n:
            n, r = divmod(n, 36)
            result = chars[r] + result
        return result or '0'

    def machine_id():
        return functools.reduce(
            lambda a, _: a + Reverse.to_string(Reverse.random_uint32()),
            [0] * 8,
            ''
        )

    def web_session_id(extra=False, c=None):
        def _p(j=6):
            a = math.floor(random.random() * 2176782336)
            a = Reverse.to_string(a)
            return '0' * (j - len(a)) + a

        if extra:
            a = _p()
            b = _p()
        else:
            a = '' # del webstorage
            b = '' # del webstorage
        if c is None:
            c = _p()
        return a + ':' + b + ':' + c

    def get_numeric_value(string):
        c = 0
        sprinkle_version = '2'

        for x in range(len(string)):
            c += ord(string[x])
        return sprinkle_version + str(c)

class Instagram:
    def __init__(self, username, user_url_follow):
        self.username = username
        self.user_url_follow = user_url_follow

        self.browser_v = random.randint(110, 120)
        self._algorithms = [
            'PKCS1WithSHA256',
            'PKCS1WithSHA384',
            'PKCS1WithSHA512',
            'PSSWithSHA256',
            'PSSWithSHA384',
            'PSSWithSHA512',
            'ECDSAWithP256AndSHA256',
            'ECDSAWithP384AndSHA384',
            'ECDSAWithP521AndSHA512'
            'PKCS1WithSHA1',
            'ECDSAWithSHA1'
        ]

        self.client = tls_client.Session(
            client_identifier=f'chrome_{self.browser_v}',
            random_tls_extension_order=True,
            supported_versions=[
                'GREASE',
                '1.3',
                '1.2',
                'P256',
                'P384'
            ],
            key_share_curves=[
                'GREASE',
                'X25519',
                'secp256r1',
                'secp384r1',
                'Unknown curve 0x11EC'
            ],
            h2_settings={
                'HEADER_TABLE_SIZE': 65536,
                'MAX_CONCURRENT_STREAMS': 1000,
                'INITIAL_WINDOW_SIZE': 6291456,
                'MAX_HEADER_LIST_SIZE': 262144
            },
            h2_settings_order=[
                'HEADER_TABLE_SIZE',
                'MAX_CONCURRENT_STREAMS',
                'INITIAL_WINDOW_SIZE',
                'MAX_HEADER_LIST_SIZE'
            ],
            supported_delegated_credentials_algorithms=self._algorithms,
            supported_signature_algorithms=self._algorithms,
            cert_compression_algo='brotli',
            ja3_string='772,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,45-11-23-51-18-65281-13-65037-27-0-35-43-10-17513-5-16,29-23-24,0',
            connection_flow=random.randint(48, 64) << 18, 
            pseudo_header_order=[
                ':authority',
                ':scheme',
                ':path'
            ],
            header_order=[
                'accept'
                'accept-language',
                'user-agent',
                'sec-ch-ua',
                'sec-fetch-dest',
                'origin'
            ]
        )

        self.client.headers = {
            "accept": "*/*",
            "accept-language": "es-US,es-419;q=0.9,es;q=0.8",
            'user-agent': f'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{self.browser_v}.0.0.0 Safari/537.36',
            "sec-ch-ua": f'"Not-A.Brand";v="8", "Chromium";v="{self.browser_v}"',
            "sec-fetch-dest": "empty",
            "sec-ch-prefers-color-scheme": "dark",
            "origin": "https://www.instagram.com",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin"
        }

        self.csrf_token = None

        self.encryption_publickey = None
        self.encryption_version = 10
        self.encryption_keysid = None

        self.resolutions = (
            (3440,1440,3440,1400),
            (1924,1007,1924,1007),
            (1920,1080,1920,1040),
            (1280,720,1280,672),
            (1920,1080,1920,1032),
            (1366,651,1366,651),
            (1366,768,1366,738),
            (1920,1080,1920,1050)
        )

        #proxy = random.choice(proxies)
        #parts = proxy.split(':')
        #proxy = f'{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}'
        proxy = None # proxy

        #self.client.proxies = {
        #    'http': proxy,
        #    'https': proxy
        #}
        #print(self.client.proxies)
        self.tempmail = TempMailAPI(proxy)
        self._initialize_signup()

    def _initialize_signup(self):
        site = self.client.get('https://www.instagram.com/accounts/emailsignup/')
        
        self.csrf_token = site.text.split('csrf_token":"')[1].split('"')[0]
        self.instagram_ajax = site.text.split('data-btmanifest="')[1].split('_')[0]
        self.app_id = site.text.split('APP_ID":"')[1].split('"')[0]
        self.asbd_id = '359341'
        self.device_id = site.text.split('_js_ig_did":{"value":"')[1].split('"')[0]
        self.session_id = Reverse.web_session_id()

        o_height, o_width, i_width, i_height = random.choice(list(self.resolutions))
        self.client.cookies['wd'] = f'{o_height}x{o_width}'

        self.encryption_publickey = site.text.split('public_key":"')[1].split('"')[0]
        self.encryption_keysid = site.text.split('key_id":"')[1].split('"')[0]

        self.client.headers.update({
            'x-asbd-id': self.asbd_id,
            'x-csrftoken': self.csrf_token,
            'x-ig-app-id': self.app_id,
            'x-ig-www-claim': '0',
            'x-mid': Reverse.machine_id(),
            'x-web-session-id': self.session_id,
            'x-web-device-id': self.device_id,
            'x-instagram-ajax': self.instagram_ajax,
            'x-requested-with': 'XMLHttpRequest'
        })
        Console.log(f'Instagram Signup {L}csrf_token={W}{self.csrf_token}', color=B, mode='inf')

    def solve_recaptcha(self):
        task_payload = {
            "clientKey": API_KEY,
            "task": {
                "type": "ReCaptchaV2TaskProxyless",
                "websiteURL": 'https://www.fbsbx.com/',
                "websiteKey": '6LdktRgnAAAAAFQ6icovYI2-masYLFjEFyzQzpix',
            }
        }
        
        create_response = requests.post("https://api.capsolver.com/createTask", json=task_payload).json()
        task_id = create_response.get("taskId")
        
        get_result_payload = {
            "clientKey": API_KEY,
            "taskId": task_id
        }

        while True:
            result_response = requests.post("https://api.capsolver.com/getTaskResult", json=get_result_payload).json()
            if result_response.get("status") == "ready":
                solution = result_response["solution"]["gRecaptchaResponse"]
                break
        return solution

    def encrypt_password(self, password):
        result = subprocess.run([
            'node',
            'pwd_encoder.js',
            str(self.encryption_keysid),
            self.encryption_publickey,
            password,
            str(round(time.time())),
            str(self.encryption_version)
        ], capture_output=True, text=True)

        return result.stdout.strip()

    def create_account(self):
        try:
            _password = secrets.token_urlsafe()
            firstname = self.username.title() + '_' + str(random.randint(100, 200000))
            user = self.username + secrets.token_hex()[:12]
            self.client.headers['content-type'] = 'application/x-www-form-urlencoded'
            captcha_token = ''
            email = self.tempmail.new_email()
 
            register_data = {
                'enc_password': self.encrypt_password(_password),
                'email': email,
                'failed_birthday_year_count': '{}',
                'first_name': firstname,
                'username': user,
                'client_id': self.client.headers['x-mid'],
                'seamless_login_enabled': '1',
                'opt_into_one_tap': False,
                'use_new_suggested_user_name': True,
                'jazoest': Reverse.get_numeric_value(self.csrf_token)
            }

            #Console.log(f'Instagram Signup {L}encrypted_pass={W}{register_data["enc_password"].split(':')[3][:30]}....', color=B, mode='inf')
            step1 = self.client.post(
                'https://www.instagram.com/api/v1/web/accounts/web_create_ajax/attempt/',
                data=register_data
            )
        
            if step1.status_code != 200:
                Console.log(f'Instagram Signup {L}message={W}{step1.json()}', color=R, mode='failed', space=2)
                return

            self.client.headers['referer'] = 'https://www.instagram.com/accounts/emailsignup/'
            self.client.cookies['ig_did'] = self.device_id
    
            birthday_data = {
                'day': random.randint(1, 30),
                'month': random.randint(1, 12),
                'year': random.randint(1980, 2007),
                'jazoest': Reverse.get_numeric_value(self.csrf_token)
            }
    
            step2 = self.client.post(
                'https://www.instagram.com/api/v1/web/consent/check_age_eligibility/',
                data=birthday_data
            )

            if step2.status_code != 200:
                Console.log(f'Instagram Signup {L}message={W}{step3.json()}', color=R, mode='failed')
                return
    
            email_data = {
                'device_id': self.client.headers['x-mid'],
                'email': email,
                'jazoest': Reverse.get_numeric_value(self.csrf_token)
            }

            step3 = self.client.post(
                'https://www.instagram.com/api/v1/accounts/send_verify_email/',
                data=email_data
            )

            if step3.status_code != 200:
                Console.log(f'Instagram Signup {L}message={W}{step3.json()}', color=R, mode='failed')
                return

            if step3.json()['require_captcha']:
                Console.log(f'Instagram Recaptcha {L}type={W}normal {L}version={W}2', color=C, mode='solving', space=1)
                captcha_token = self.solve_recaptcha()
    
                Console.log(f'Instagram Recaptcha {L}token={W}{captcha_token[:40]}....', color=G, mode='solver', space=2)
    
            sendverify = self.client.post(
                'https://www.instagram.com/api/v1/accounts/send_verify_email/',
                data={
                    'captcha_token': captcha_token,
                    'device_id': self.client.headers['x-mid'],
                    'email': email,
                    'jazoest': Reverse.get_numeric_value(self.csrf_token)
                }
            )
    
            if sendverify.status_code != 200:
                Console.log(f'Instagram Signup {L}message={W}{sendverify.json()}', color=R, mode='failed', space=2)
                return

            code = self.tempmail.get_verification_code()
            
            print('code', code)

            verify_data = {
                'code': code,
                'device_id': self.client.headers['x-mid'],
                'email': email,
                'jazoest': Reverse.get_numeric_value(self.csrf_token)
            }

            verify = self.client.post(
                'https://www.instagram.com/api/v1/accounts/check_confirmation_code/',
                data=verify_data
            )

            if verify.status_code != 200:
                Console.log(f'Instagram Email {L}message={W}{verify.json()}', color=R, mode='failed', space=2)
                return

            signup_code = verify.json()['signup_code']
            self.session_id = Reverse.web_session_id(extra=True, c=self.session_id.split(':')[2])
            register_data.update({
                'tos_version': 'eu',
                'force_sign_up_code': signup_code,
                'extra_session_id': self.session_id,
                **birthday_data
            })

            create = self.client.post(
                'https://www.instagram.com/api/v1/web/accounts/web_create_ajax/',
                data=register_data
            )

            if create.status_code == 200 and create.json()['account_created']:
                data = create.json()
                Console.log(f'Instagram Signup {L}username={W}{firstname} {L}user_id={W}{data["user_id"]}', color=P, mode='account', space=1)
                del self.client.cookies['rur']
                open('accounts.txt', 'a+').write(f'{user}:{_password}\n')
                print(self.client.cookies)
                
                q = self.client.get('https://www.instagram.com/', allow_redirects=True)
                print(q.url)
                print(q)
            else:
                Console.log(f'Instagram Signup {L}message={W}{create.json()["errors"]}', color=R, mode='failed', space=2)
        except Exception as e:
            print(e)

    def solve_verification(self):
        
        auth_html = ''
        apc_token = None
        
        rev = auth_html.split('"rev":')[1].split(']')[0]
        hsi = auth_html.split('"brsid":"')[1].split('"')[0]
        timestamp = auth_html.split('"serverTime":')[1].split(',')[0]
        variables = json.dumps({
            'apc': apc_token,
            'device_id': None
        }, separators=(':', ','))
        
        payload = {
            'av': '0',
            '__d': 'www',
            '__user': '0',
            '__a': '1',
            '__req': 'l',
            '__hs': '20251.HYP:instagram_web_pkg.2.1...0',
            'dpr': '1',
            '__ccg': 'GOOD',
            '__rev': rev,
            '__s': self.session_id,
            '__hsi': hsi,
            '__dyn': '7xeUmwlE7ibwKBAg5S1Dxu13w8CewSwMwNw9G2S0lW4o0B-q1ew6ywaq0yE7i0n24o5-1ywOwv89k2C1Fwc60D82Ixe0EUjwGzEaE2iwNwmE2eU5O0HU1IEGdwtU662O0Lo6-3u2WE15E6O1FwlA1HQp1yU5Oi2K7E5y1rwdy9w5awFw',
            '__csr': 'gkNlIhlgxEAznStrhlmCVyaRAKXDleaXyrmESuFoapVUrxa2Wdx27potzUGaAmdyCu4qCBxO9Jk-inhXhU8V8sCCxvxW3K3Py8gxi4HyoCEKcCwSK8wNy8eqw05tOpoy0Q82hwdYje0J6051o0l2w1ke5e0qx02FCEig5eBgvg02ojw1gq',
            '__comet_req': '7',
            'lsd': 'AVqcy_QAeRU',
            'jazoest': Reverse.get_numeric_value(self.csrf_token),
            '__spin_r': '1023776669',
            '__spin_b': 'trunk',
            '__spin_t': timestamp,
            '__crn': 'comet.igweb.PolarisAuthPlatformCodeEntryRoute',
            'fb_api_caller_class': 'RelayModern',
            'fb_api_req_friendly_name': 'AuthPlatformApproveFromAnotherDevicePollingMutation',
            'variables': variables,
            'doc_id': '9933492023382430'
        }
        
        send_code = self.client.post(
            'https://www.instagram.com/api/graphql',
            data=payload
        )
        
        

if __name__ == '__main__':
    max_threads = 3

    def _run_thread():
        ig = Instagram(
            username='Patikk',
            user_url_follow='https://www.instagram.com/fr/'
        )
        ig.create_account()

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        for i in range(5):
            executor.submit(_run_thread)
