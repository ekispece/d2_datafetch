#!/usr/bin/python
import requests
import time
from dota2py import api as dota_api
from d2_db import db
from hero import Hero
# import match_details_fetcher as mdf

skill = 3

dota_api.set_api_key("")  # When possible do substitute this key by your own


def fetch_match_history_per_hero(hero_id, start_from=None):
    global skill
    # first we get the results from match_history
    try:
        if start_from is None:
            match_history = dota_api.get_match_history(skill=skill, hero_id=hero_id)
        else:
            match_history = dota_api.get_match_history(skill=skill, hero_id=hero_id, start_at_match_id=start_from)

        return extract_match_history_info(match_history)

    except requests.HTTPError:
        print ("Server error")
        return None
    except requests.ConnectionError:
        print ("connection error")
        return None


def extract_match_history_info(match_history_info):
        return match_history_info["result"]["matches"]


database = db.get_database()

match_history_collection = database.match_ids
heroes_collection = database.heroes
if heroes_collection.find_one() is None:
    import mount_db  # this should mount the necessary collections

hero_list = []
for a_hero in heroes_collection.find():
    hero_list.append(Hero(a_hero))

# print "I get to here"

while True:
    for hero in hero_list:
        print ("Getting matches for hero : " + str(hero.localized_name))
        matches_per_hero = fetch_match_history_per_hero(hero_id=hero.id)
        if matches_per_hero is None:
            print("Sleeping for 10 mins seeing if server gets back to normal")
            time.sleep(10*60)
            break

        for i in range(0, 5):
            last_match = None
            if matches_per_hero is None:
                print("Sleeping for 10 mins seeing if server gets back to normal")
                time.sleep(10 * 60)
                break
            for a_match in matches_per_hero:
                if "lobby_type" in a_match and a_match["lobby_type"] in [0, 2, 5, 6, 7]:  # We are only interested in 5x5 games
                    match_relevant_info = {"match_id": a_match["match_id"]}
                    if match_history_collection.find_one({"match_id": a_match["match_id"]}) is None:
                        match_relevant_info["fetched"] = False
                        match_history_collection.insert_one(match_relevant_info)
                    else:
                        continue
                        # match_parsed = True
                        # break

                last_match = a_match["match_id"]

            # if match_parsed:
            #     break

            matches_per_hero = fetch_match_history_per_hero(hero_id=hero.id, start_from=last_match)

    print ("parsing matches")

    # mdf.parse_matches()

    print ("Fetched matches for now, sleeping for 30m")
    time.sleep(60 * 30)
