class Rank:
    def __init__(self, request, log):
        self.Requests = request
        self.log = log

    def get_rank(self, puuid, season_id):
        response = self.Requests.fetch('pd', f"/mmr/v1/players/{puuid}", "get")
        try:
            if response:
                self.log.debug("retrieved rank successfully")
                r = response
                rank_tier = r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][season_id]["CompetitiveTier"]
                if int(rank_tier) >= 21:
                    rank = [rank_tier,
                            r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][season_id]["RankedRating"],
                            r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][season_id]["LeaderboardRank"], ]
                elif int(rank_tier) not in (0, 1, 2, 3):
                    rank = [rank_tier,
                            r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][season_id]["RankedRating"],
                            0,
                            ]
                else:
                    rank = [0, 0, 0]

            else:
                self.log.error("failed getting rank")
                self.log.error(response.text)
                rank = [0, 0, 0]
        except TypeError:
            rank = [0, 0, 0]
        except KeyError:
            rank = [0, 0, 0]
        max_rank = 0
        seasons = r["QueueSkills"]["competitive"].get("SeasonalInfoBySeasonID")
        if seasons is not None:
            for season in r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"]:
                if r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][season]["WinsByTier"] is not None:
                    for winByTier in r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][season]["WinsByTier"]:
                        if int(winByTier) > max_rank:
                            max_rank = int(winByTier)
            rank.append(max_rank)
        else:
            rank.append(max_rank)
        return [rank, response]
