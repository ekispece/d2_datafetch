#!/usr/bin/python
from dota2py import api as dota_api
from d2_db import db
from multiprocessing.dummy import Pool as ThreadPool
from requests import exceptions

pool = ThreadPool(100)


def get_match_details(match_id):
    dota_api.set_api_key("3A315E5FE932409684A1C2DB288A92C6")  # When possible do substitute this key by your own
    return extract_match_details_info(dota_api.get_match_details(match_id=match_id))


def extract_match_details_info(json):
    return json["result"]


def remove_useless_info(match_detail):
    if match_detail["radiant_win"]:
        match_detail["winner"] = "radiant"
    else:
        match_detail["winner"] = "dire"
    del match_detail["radiant_win"]  # This is a dumb label, It's important, but needs more readability
    del match_detail["start_time"]
    del match_detail["match_seq_num"]
    del match_detail["duration"]
    del match_detail["tower_status_radiant"]
    del match_detail["tower_status_dire"]
    del match_detail["barracks_status_radiant"]
    del match_detail["barracks_status_dire"]
    del match_detail["cluster"]
    del match_detail["first_blood_time"]
    del match_detail["human_players"]
    del match_detail["leagueid"]
    del match_detail["positive_votes"]
    del match_detail["negative_votes"]
    del match_detail["flags"]
    del match_detail["engine"]
    del match_detail["radiant_score"]
    del match_detail["dire_score"]
    for player_info in match_detail["players"]:
        if player_info["hero_id"] == 0:
            del player_info
            continue
        if player_info["player_slot"] < 100:
            player_info["team"] = "radiant"
        else:
            player_info["team"] = "dire"
        del player_info["gold"]
        del player_info["gold_spent"]
        if "ability_upgrades" in player_info:
            del player_info["ability_upgrades"]
    return match_detail


# print str(match_id_collection.find().count())
# for match_id in match_id_collection.find():
def parse_match(match_id):
    if match_details_collection.find_one({"match_id": match_id["match_id"]}):
        return  # This match is already saved
    try:
        match_detail = remove_useless_info(get_match_details(match_id["match_id"]))
        match_details_collection.insert_one(match_detail)
        match_id_collection.update_one({"match_id": match_id["match_id"]},
                                       {
                                           "$set": {
                                               "fetched": True
                                           }
                                       })
    except exceptions.HTTPError:
        print "Server or request error. Match was not parsed, continuing"
        return


# Go through every match_id available on the db
database = db.get_database()
match_id_collection = database.match_ids
match_details_collection = database.match_details

pool.map(parse_match, match_id_collection.find({"fetched": False}))
