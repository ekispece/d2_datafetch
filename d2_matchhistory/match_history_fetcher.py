#!/usr/bin/python
from dota2py import api as dota_api
from d2_db import db
from hero import Hero


class MatchHistoryFetcher:
    skill = 3

    def __init__(self):
        dota_api.set_api_key("3A315E5FE932409684A1C2DB288A92C6")  # When possible do substitute this key by your own

    def fetch_match_history_per_hero(self, hero_id, start_from=None):
        # first we get the results from match_history
        if start_from is None :
            match_history = dota_api.get_match_history(skill=self.skill, hero_id=hero_id)
        else:
            match_history = dota_api.get_match_history(skill=self.skill, hero_id=hero_id, start_at_match_id=start_from)

        return self.extract_match_history_info(match_history)

    @staticmethod
    def extract_match_history_info(match_history_info):
        return match_history_info["result"]["matches"]


matches = MatchHistoryFetcher()
matches.fetch_match_history_per_hero(1)

database = db.get_database()

match_history_collection = database.match_ids
heroes_collection = database.heroes
if heroes_collection.find_one() is None:
    import mount_db  # this should mount the necessary collections

for a_hero in heroes_collection.find():
    match_parsed = False
    hero = Hero(a_hero)
    print "Getting matches for hero : " + str(hero.localized_name)
    matches_per_hero = matches.fetch_match_history_per_hero(hero_id=hero.id)
    for i in xrange(0, 5):
        last_match = None
        for a_match in matches_per_hero:
            if "lobby_type" in a_match and a_match["lobby_type"] in [0, 2, 5, 6, 7]:  # We are only interested in 5x5 games
                match_relevant_info = {"match_id": a_match["match_id"]}
                if match_history_collection.find_one({"match_id": a_match["match_id"]}) is None:
                    match_relevant_info["fetched"] = False
                    match_history_collection.insert_one(match_relevant_info)
                else:
                    match_parsed = True
                    break

            last_match = a_match["match_id"]

        if match_parsed:
            break

        matches_per_hero = matches.fetch_match_history_per_hero(hero_id=hero.id, start_from=last_match)
