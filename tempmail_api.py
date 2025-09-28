import sys
import time
import httpx

class TempMailAPI:
    def __init__(self, proxy) -> None:
        self.api = 'http://www.disposablemail.com'
        self.client = httpx.Client(follow_redirects=True, timeout=20)
        if proxy is not None:
            self.client.proxies = {
                'http': proxy,
                'https': proxy
            }
        #self.client.headers = {
        #    'x-requested-with': 'XMLHttpRequest'
        #}

        self.attempt = 0
        self.email = None

    def _setup(self) -> None:
        site = self.client.get(self.api)
        self.csrf = site.text.split('CSRF="')[1].split('"')[0]

        self.client.cookies = site.cookies

    def new_email(self) -> str:
        self._setup()
        self.client.headers = {
            'x-requested-with': 'XMLHttpRequest'
        }

        email_data = self.client.get(f'{self.api}/index/index/?csrf_token={self.csrf}').text
        self.email = str(email_data).split('{"email":"')[1].split('","heslo"')[0]
        return self.email

    def get_verification_code(self):
        code = None 
        while not code or self.attempt >= 25:
            messages = self.client.get(f'{self.api}/index/refresh')

            for message in messages.json():
                index_id = message['id']

                if index_id in [2, 3]:
                    window = self.client.get(f'{self.api}/email/id/{index_id}/')
                    code = window.text
                    break
                
                self.attempt += 1
                time.sleep(1)
        
        code = code.split('padding-bottom:25px;">')[1].split('</td><')[0]
        return code

if __name__ == '__main__':
    temp = TempMailAPI()
    print(temp.new_email())
