from copy import deepcopy

from d2_db import db


def start():
    database = db.get_database()
    heroes_list_collection = database.heroes
    match_details_collection = database.match_details
    heroes_metrics_collection = database.heroes_metrics
    items_list_collection = database.items

    heroes = {}
    items = {}

    for item in items_list_collection.find():
        items[item["id"]] = {"bought": 0L}

    for hero in heroes_list_collection.find():
        heroes[hero["id"]] = {
            "wins": 0L,
            "games": 0L,
            "won_match_duration": 0L,
            "gold": 0L,
            "xp": 0L,
            "tower_damage": 0L,
            "hero_damage": 0L,
            "hero_healing": 0L,
            "last_hits": 0L,
            "denies": 0L,
            "kills": 0L,
            "deaths": 0L,
            "assists": 0L,
            "items": deepcopy(items)
        }

    for a_match in match_details_collection.find():
        winner = a_match["winner"]
        for player in a_match["players"]:
            if player["team"] == winner:
                heroes[player["hero_id"]]["wins"] += 1
                heroes[player["hero_id"]]["won_match_duration"] += a_match["duration"]

            heroes[player["hero_id"]]["games"] += 1
            heroes[player["hero_id"]]["gold"] += player["gold_per_min"]
            heroes[player["hero_id"]]["xp"] += player["xp_per_min"]
            heroes[player["hero_id"]]["tower_damage"] += player["tower_damage"]
            heroes[player["hero_id"]]["hero_damage"] += player["hero_damage"]
            heroes[player["hero_id"]]["hero_healing"] += player["hero_healing"]
            heroes[player["hero_id"]]["last_hits"] += player["last_hits"]
            heroes[player["hero_id"]]["denies"] += player["denies"]
            heroes[player["hero_id"]]["kills"] += player["kills"]
            heroes[player["hero_id"]]["deaths"] += player["deaths"]
            heroes[player["hero_id"]]["assists"] += player["assists"]
            for item in player["items"]:
                heroes[player["hero_id"]]["items"][item["item_id"]]["bought"] += 1

    for k, v in heroes.iteritems():
        heroes_metrics_collection.insert_one({
            "hero_id": k,
            "wins": v["wins"],
            "games": v["games"],
            "won_match_duration": v["won_match_duration"],
            "gold": v["gold"],
            "xp": v["xp"],
            "tower_damage": v["tower_damage"],
            "hero_damage": v["hero_damage"],
            "hero_healing": v["hero_healing"],
            "last_hits": v["last_hits"],
            "denies": v["denies"],
            "kills": v["kills"],
            "deaths": v["deaths"],
            "assists": v["assists"],
            "items": {str(k): i for k, i in v["items"].iteritems() if i["bought"] > 0}
        })

        # "wins": 0L,
        # "games": 0L,
        # "won_match_duration": 0L,
        # "gold": 0L,
        # "xp": 0L,
        # "tower_damage": 0L,
        # "hero_damage": 0L,
        # "hero_healing": 0L,
        # "last_hits": 0L,
        # "denies": 0L,
        # "kills": 0L,
        # "deaths": 0L,
        # "assists": 0L,
        # "items": deepcopy(items)
