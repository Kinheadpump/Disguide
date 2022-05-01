import base64
import json
import time


class Presences:
    def __init__(self, fetcher, logger):
        self.fetcher = fetcher
        self.logger = logger

    def get_presence(self):
        presences = self.fetcher.fetch(url_type="local", endpoint="/chat/v4/presences", method="get")
        self.logger.debug(f"fetched presences")
        return presences['presences']

    def get_game_state(self, presences):
        for presence in presences:
            if presence['puuid'] == self.fetcher.puuid:
                if presence.get("championId") is not None or presence.get("product") == "league_of_legends":
                    return None
                else:
                    return json.loads(base64.b64decode(presence['private']))["sessionLoopState"]

    def decode_presence(self, private):
        if "{" not in str(private) and private is not None and str(private) != "":
            decode_dict = json.loads(base64.b64decode(str(private)).decode("utf-8"))
            if decode_dict.get("isValid"):
                return decode_dict
        return {
            "isValid": False,
            "partyId": 0,
            "partySize": 0,
            "partyVersion": 0,
        }

    def wait_for_presence(self, players_puuids):
        while True:
            presence = self.get_presence()
            for puuid in players_puuids:
                if puuid not in str(presence):
                    time.sleep(1)
                    continue
            break
