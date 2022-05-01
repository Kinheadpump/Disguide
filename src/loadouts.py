import time
import requests
from src.constants import sockets


class Loadouts:
    def __init__(self, fetcher, log):
        self.fetcher = fetcher
        self.log = log

    def get_match_loadouts(self, match_id, players, weapon_choose, valo_api_skins, names, state="game"):
        players_backup = players
        weapon_lists = {}
        valo_api_weapons = requests.get("https://valorant-api.com/v1/weapons").json()
        if state == "game":
            team_id = "Blue"
            player_inventories = self.fetcher.fetch("glz", f"/core-game/v1/matches/{match_id}/loadouts", "get")
        elif state == "pregame":
            pregame_stats = players
            players = players["AllyTeam"]["Players"]
            team_id = pregame_stats['Teams'][0]['TeamID']
            player_inventories = self.fetcher.fetch("glz", f"/pregame/v1/matches/{match_id}/loadouts", "get")
        for player in range(len(players)):
            if team_id == "Red":
                invindex = player + len(players) - len(player_inventories["Loadouts"])
            else:
                invindex = player
            inv = player_inventories["Loadouts"][invindex]
            if state == "game":
                inv = inv["Loadout"]
            for weapon in valo_api_weapons["data"]:
                if weapon["displayName"].lower() == weapon_choose.lower():
                    skin_id = \
                        inv["Items"][weapon["uuid"].lower()]["Sockets"]["bcef87d6-209b-46c6-8b19-fbe40bd95abc"]["Item"][
                            "ID"]
                    for skin in valo_api_skins.json()["data"]:
                        if skin_id.lower() == skin["uuid"].lower():
                            weapon_lists.update({players[player]["Subject"]: skin["displayName"]})
        final_json = self.convert_loadout_to_json_array(player_inventories, players_backup, state, names)
        return weapon_lists

    def convert_loadout_to_json_array(self, player_inventories, players, state, names):
        valo_api_sprays = requests.get("https://valorant-api.com/v1/sprays")
        valo_api_weapons = requests.get("https://valorant-api.com/v1/weapons")
        valo_api_buddies = requests.get("https://valorant-api.com/v1/buddies")
        valo_api_agents = requests.get("https://valorant-api.com/v1/agents")
        valo_api_titles = requests.get("https://valorant-api.com/v1/playertitles")
        valo_api_player_cards = requests.get("https://valorant-api.com/v1/playercards")
        self.log.debug("got val apis")
        final_final_json = {"Players": {}}

        final_final_json.update({"time": int(time.time())})
        final_json = final_final_json["Players"]
        if state == "game":
            player_inventories = player_inventories["Loadouts"]
            for i in range(len(player_inventories)):
                player_inventory = player_inventories[i]["Loadout"]
                final_json.update(
                    {
                        players[i]["Subject"]: {}
                    }
                )
                self.log.debug("created name field")
                final_json[players[i]["Subject"]].update({"Name": names[players[i]["Subject"]]})
                final_json[players[i]["Subject"]].update({"Sprays": {}})
                self.log.debug("append sprays to field")

                final_json[players[i]["Subject"]].update({"Level": players[i]["PlayerIdentity"]["AccountLevel"]})

                for title in valo_api_titles.json()["data"]:
                    if title["uuid"] == players[i]["PlayerIdentity"]["PlayerTitleID"]:
                        final_json[players[i]["Subject"]].update({"Title": title["titleText"]})

                for PCard in valo_api_player_cards.json()["data"]:
                    if PCard["uuid"] == players[i]["PlayerIdentity"]["PlayerCardID"]:
                        final_json[players[i]["Subject"]].update({"PlayerCard": PCard["largeArt"]})

                for agent in valo_api_agents.json()["data"]:
                    if agent["uuid"] == players[i]["CharacterID"]:
                        final_json[players[i]["Subject"]].update({"AgentArtworkName": agent["displayName"] + "Artwork"})
                        final_json[players[i]["Subject"]].update({"Agent": agent["displayIcon"]})

                for j in range(len(player_inventory["Sprays"]["SpraySelections"])):
                    spray = player_inventory["Sprays"]["SpraySelections"][j]
                    final_json[players[i]["Subject"]]["Sprays"].update({j: {}})
                    for sprayValApi in valo_api_sprays.json()["data"]:
                        if spray["SprayID"] == sprayValApi["uuid"]:
                            final_json[players[i]["Subject"]]["Sprays"][j].update({
                                "displayName": sprayValApi["displayName"],
                                "displayIcon": sprayValApi["displayIcon"],
                                "fullTransparentIcon": sprayValApi["fullTransparentIcon"]
                            })

                self.log.debug("create weapons field")
                final_json[players[i]["Subject"]].update({"Weapons": {}})

                for skin in player_inventory["Items"]:
                    self.log.debug("create skin field")
                    final_json[players[i]["Subject"]]["Weapons"].update({skin: {}})

                    for socket in player_inventory["Items"][skin]["Sockets"]:
                        self.log.debug("predefined sockets")
                        for var_socket in sockets:
                            if socket == sockets[var_socket]:
                                final_json[players[i]["Subject"]]["Weapons"][skin].update(
                                    {
                                        var_socket: player_inventory["Items"][skin]["Sockets"][socket]["Item"]["ID"]
                                    }
                                )

                    self.log.debug("buddies")
                    for socket in player_inventory["Items"][skin]["Sockets"]:
                        if sockets["skin_buddy"] == socket:
                            for buddy in valo_api_buddies.json()["data"]:
                                if buddy["uuid"] == player_inventory["Items"][skin]["Sockets"][socket]["Item"]["ID"]:
                                    final_json[players[i]["Subject"]]["Weapons"][skin].update(
                                        {
                                            "buddy_displayIcon": buddy["displayIcon"]
                                        }
                                    )

                    self.log.debug("append names to field")
                    for weapon in valo_api_weapons.json()["data"]:
                        if skin == weapon["uuid"]:
                            final_json[players[i]["Subject"]]["Weapons"][skin].update(
                                {
                                    "weapon": weapon["displayName"]
                                }
                            )
                            for skinValApi in weapon["skins"]:
                                if skinValApi["uuid"] == \
                                        player_inventory["Items"][skin]["Sockets"][sockets["skin"]]["Item"]["ID"]:
                                    final_json[players[i]["Subject"]]["Weapons"][skin].update(
                                        {
                                            "skinDisplayName": skinValApi["displayName"]
                                        }
                                    )
                                    for chroma in skinValApi["chromas"]:
                                        if chroma["uuid"] == \
                                                player_inventory["Items"][skin]["Sockets"][sockets["skin_chroma"]][
                                                    "Item"]["ID"]:
                                            if chroma["displayIcon"] is not None:
                                                final_json[players[i]["Subject"]]["Weapons"][skin].update(
                                                    {
                                                        "skinDisplayIcon": chroma["displayIcon"]
                                                    }
                                                )
                                            elif chroma["fullRender"] is not None:
                                                final_json[players[i]["Subject"]]["Weapons"][skin].update(
                                                    {
                                                        "skinDisplayIcon": chroma["fullRender"]
                                                    }
                                                )
                                            elif skinValApi["displayIcon"] is not None:
                                                final_json[players[i]["Subject"]]["Weapons"][skin].update(
                                                    {
                                                        "skinDisplayIcon": skinValApi["displayIcon"]
                                                    }
                                                )
                                            else:
                                                final_json[players[i]["Subject"]]["Weapons"][skin].update(
                                                    {
                                                        "skinDisplayIcon": skinValApi["levels"][0]["displayIcon"]
                                                    }
                                                )
                                    if skinValApi["displayName"].startswith("Standard") or skinValApi["displayName"]\
                                            .startswith("Melee"):
                                        final_json[players[i]["Subject"]]["Weapons"][skin]["skinDisplayIcon"] = weapon[
                                            "displayIcon"]
        return final_final_json
