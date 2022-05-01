class PreGame:
    def __init__(self, fetcher, log):
        self.log = log
        self.fetcher = fetcher
        self.response = ""

    def get_pre_game_match_id(self):
        try:
            self.response = self.fetcher.fetch(url_type="glz", endpoint=f"/pregame/v1/players/{self.fetcher.puuid}",
                                               method="get")
            match_id = self.response['MatchID']
            self.log.debug(f"retrieved pregame match id: '{match_id}'")
            return match_id
        except (KeyError, TypeError):
            self.log.error(f"cannot find pregame match id: ")
            return 0

    def get_pre_game_stats(self):
        return self.fetcher.fetch("glz", f"/pregame/v1/matches/{self.get_pre_game_match_id()}", "get")
