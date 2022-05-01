class CoreGame:
    def __init__(self, fetcher, log):
        self.log = log
        self.fetcher = fetcher
        self.response = ""

    def get_core_game_match_id(self):
        try:
            self.response = self.fetcher.fetch(url_type="glz", endpoint=f"/core-game/v1/players/{self.fetcher.puuid}",
                                               method="get")
            match_id = self.response['MatchID']
            self.log.debug(f"retrieved coregame match id: '{match_id}'")
            return match_id
        except (KeyError, TypeError):
            self.log.error(f"cannot find coregame match id: ")
            return 0

    def get_core_game_stats(self):
        return self.fetcher.fetch(url_type="glz", endpoint=f"/core-game/v1/matches/{self.get_core_game_match_id()}",
                                  method="get")
