import base64
import json
import time

import requests
import os

from src.errors import Error


class Fetch:
    def __init__(self, logger):
        self.logger = logger

        self.headers = {}
        self.region = self.get_region()
        self.lockfile = self.get_lockfile()

        self.pd_url = f"https://pd.{self.region[0]}.a.pvp.net"
        self.glz_url = f"https://glz-{self.region[1][0]}.{self.region[1][1]}.a.pvp.net"
        self.logger.debug(f"Api urls: pd_url: '{self.pd_url}', glz_url: '{self.glz_url}'")
        self.region = self.region[0]

        self.puuid = ''
        self.get_headers()

    def get_lockfile(self):
        path = os.path.join(os.getenv('LOCALAPPDATA'), R'Riot Games\Riot Client\Config\lockfile')
        if not Error(self.logger).lockfile_error(path):
            with open(path) as lockfile:
                self.logger.debug("opened log file")
                data = lockfile.read().split(':')
                keys = ['name', 'PID', 'port', 'password', 'protocol']
                return dict(zip(keys, data))

    def get_region(self):
        path = os.path.join(os.getenv('LOCALAPPDATA'), R'VALORANT\Saved\Logs\ShooterGame.log')
        with open(path, "r", encoding="utf8") as file:
            while True:
                line = file.readline()
                if '.a.pvp.net/account-xp/v1/' in line:
                    pd_url = line.split('.a.pvp.net/account-xp/v1/')[0].split('.')[-1]
                elif 'https://glz' in line:
                    glz_url = [(line.split('https://glz-')[1].split(".")[0]),
                               (line.split('https://glz-')[1].split(".")[1])]
                if "pd_url" in locals().keys() and "glz_url" in locals().keys():
                    return [pd_url, glz_url]

    def get_current_version(self):
        path = os.path.join(os.getenv('LOCALAPPDATA'), R'VALORANT\Saved\Logs\ShooterGame.log')
        with open(path, "r", encoding="utf8") as file:
            while True:
                line = file.readline()
                if 'CI server version:' in line:
                    version_without_shipping = line.split('CI server version: ')[1].strip()
                    version = version_without_shipping.split("-")
                    version.insert(2, "shipping")
                    version = "-".join(version)
                    self.logger.debug(f"got version from logs '{version}'")
                    return version

    def get_headers(self):
        if self.headers == {}:
            local_headers = {'Authorization': 'Basic ' + base64.b64encode(
                ('riot:' + self.lockfile['password']).encode()).decode()}
            response = requests.get(f"https://127.0.0.1:{self.lockfile['port']}/entitlements/v1/token",
                                    headers=local_headers, verify=False)
            entitlements = response.json()
            self.puuid = entitlements['subject']
            headers = {
                'Authorization': f"Bearer {entitlements['accessToken']}",
                'X-Riot-Entitlements-JWT': entitlements['token'],
                'X-Riot-ClientPlatform': "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjog"
                                         "IldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5"
                                         "MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9",
                'X-Riot-ClientVersion': self.get_current_version(),
                "User-Agent": "ShooterGame/13 Windows/10.0.19043.1.256.64bit"
            }
            return headers

    def fetch(self, url_type, endpoint, method, body=None):
        try:
            if url_type == "glz":
                response = requests.request(method, self.glz_url + endpoint, headers=self.get_headers(), verify=False,
                                            data=body)
                self.logger.debug(f"response code: {response.status_code}")
                if not response.ok:
                    time.sleep(5)
                    self.headers = {}
                    self.fetch(url_type, endpoint, method)
                return response.json()
            elif url_type == "pd":
                response = requests.request(method, self.pd_url + endpoint, headers=self.get_headers(), verify=False,
                                            data=body)
                self.logger.debug(f"response code: {response.status_code}")
                if not response.ok:
                    time.sleep(5)
                    self.headers = {}
                    self.fetch(url_type, endpoint, method)
                return response.json()
            elif url_type == "local":
                local_headers = {'Authorization': 'Basic ' + base64.b64encode(
                    ('riot:' + self.lockfile['password']).encode()).decode()}
                response = requests.request(method, f"https://127.0.0.1:{self.lockfile['port']}{endpoint}",
                                            headers=local_headers,
                                            verify=False,
                                            data=body)
                self.logger.debug(f"response code: {response.status_code}")
                return response.json()
            elif url_type == "custom":
                response = requests.request(method, f"{endpoint}", headers=self.get_headers(), verify=False, data=body)
                self.logger.debug(f"response code: {response.status_code}")
                if not response.ok:
                    self.headers = {}
                return response.json()
            self.logger.debug(f"fetch: url: '{url_type}', endpoint: {endpoint}, method: {method}")
        except json.decoder.JSONDecodeError:
            self.logger.error(f"JSONDecodeError in fetch function")
