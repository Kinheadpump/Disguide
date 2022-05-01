import requests


class Maps:
    def __init__(self, fetcher, log):
        self.fetcher = fetcher
        self.log = log

    def get_name_from_id(self, map_id):
        response = requests.get("https://valorant-api.com/v1/maps")
        if response.status_code == 200:
            self.log.debug("retrieving maps")
            for val_map in response.json()["data"]:
                if val_map["mapUrl"] == map_id:
                    return val_map["displayName"]
        else:
            self.log.error("couldn't get maps")
