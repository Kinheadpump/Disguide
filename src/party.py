import requests


class Party:
    def __init__(self, fetcher, logger):
        self.fetcher = fetcher
        self.logger = logger

    def get_current_party_id(self):
        self.logger.debug("fetching party ID")
        headers = self.fetcher.get_headers()

        region = self.fetcher.region
        puuid = self.fetcher.puuid

        url = f'https://glz-{region}-1.{region}.a.pvp.net/parties/v1/players/{puuid}'

        session = requests.get(url, headers=headers)

        return session.json()

    def get_party(self, pid):
        self.logger.debug("fetching party ID")
        headers = self.fetcher.get_headers()

        region = self.fetcher.region
        puuid = self.fetcher.puuid

        url = f'https://glz-{region}-1.{region}.a.pvp.net/parties/v1/parties/{pid}'

        session = requests.get(url, headers=headers)

        return session.json()