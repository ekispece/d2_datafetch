#!/usr/bin/python
from dota2py import api as dota_api
from d2_db import db
from multiprocessing.dummy import Pool as ThreadPool
from requests import exceptions
import json

pool = ThreadPool(10)


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
    del match_detail["game_mode"]
    del match_detail["lobby_type"]
    del match_detail["radiant_win"]  # This is a dumb label, It's important, but needs more readability
    del match_detail["start_time"]
    del match_detail["match_seq_num"]
    if match_detail["duration"] < 15 * 60:
        # print "match lasted less than 15 min"
        return None
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
        if "team" not in player_info:
            # print "Not all players connected"
            return None  # this match is non-existent
        del player_info["player_slot"]
        del player_info["level"]
        del player_info["gold"]
        if "leaver_status" in player_info:
            if player_info["leaver_status"] > 1:  # 0 no abandon, 1 DC but no abandon, 2 onwards abandon
                # print "a player abandoned the match"
                return None
            del player_info["leaver_status"]
        del player_info["gold_spent"]
        if "ability_upgrades" in player_info:
            del player_info["ability_upgrades"]
        useless_items = [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 237, 12, 182, 246, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22,
                         23, 24, 25, 27, 28, 29, 31, 32, 33, 34, 35, 38, 216, 39, 40, 42, 43, 217, 218, 241, 45, 46, 47,
                         219, 48, 220, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 66, 67, 68, 69,
                         70, 71, 72, 74, 76, 78, 80, 84, 85, 86, 87, 88, 89, 91, 93, 94, 95, 97, 99, 233, 101, 103, 197,
                         198, 199, 200, 105, 191, 192, 107, 109, 111, 113, 115, 117, 118, 120, 122, 221, 124, 243, 126,
                         128, 129, 130, 132, 134, 136, 138, 140, 142, 144, 146, 148, 234, 150, 183, 248, 153, 155, 157,
                         159, 161, 163, 165, 167, 169, 171, 173, 195, 175, 177, 179, 228, 184, 186, 227, 188, 189, 230,
                         205, 238, 239, 207, 209, 211, 213, 214, 215, 253, 1000, 1001, 1002, 1003, 1004, 1005, 1006,
                         1007, 1008, 1009, 1010, 1011, 1012, 1013, 1014, 1015, 1016, 1017, 1018, 1019, 1020]
        items = []
        # thanks steamApi for this shitty interface
        if player_info["item_0"] not in useless_items:
            items.append({"item_id": player_info["item_0"]})
        if player_info["item_1"] not in useless_items:
            items.append({"item_id": player_info["item_1"]})
        if player_info["item_2"] not in useless_items:
            items.append({"item_id": player_info["item_2"]})
        if player_info["item_3"] not in useless_items:
            items.append({"item_id": player_info["item_3"]})
        if player_info["item_4"] not in useless_items:
            items.append({"item_id": player_info["item_4"]})
        if player_info["item_5"] not in useless_items:
            items.append({"item_id": player_info["item_5"]})
        del player_info["item_0"]
        del player_info["item_1"]
        del player_info["item_2"]
        del player_info["item_3"]
        del player_info["item_4"]
        del player_info["item_5"]
        if "additional_units" in player_info:
            for additional_unit in player_info["additional_units"]:
                if additional_unit["unitname"] == "spirit_bear":
                    if additional_unit["item_0"] not in useless_items:
                        items.append({"item_id": additional_unit["item_0"]})
                    if additional_unit["item_1"] not in useless_items:
                        items.append({"item_id": additional_unit["item_1"]})
                    if additional_unit["item_2"] not in useless_items:
                        items.append({"item_id": additional_unit["item_2"]})
                    if additional_unit["item_3"] not in useless_items:
                        items.append({"item_id": additional_unit["item_3"]})
                    if additional_unit["item_4"] not in useless_items:
                        items.append({"item_id": additional_unit["item_4"]})
                    if additional_unit["item_5"] not in useless_items:
                        items.append({"item_id": additional_unit["item_5"]})
            del player_info["additional_units"]
        player_info["items"] = items

    return match_detail


# print str(match_id_collection.find().count())
# for match_id in match_id_collection.find():
def parse_match(match_id):
    global match_details_collection
    global match_id_collection
    if match_details_collection.find_one({"match_id": match_id["match_id"]}):
        return  # This match is already saved
    try:
        match_detail = remove_useless_info(get_match_details(match_id["match_id"]))
        match_id_collection.update_one({"match_id": match_id["match_id"]},
                                       {
                                           "$set": {
                                               "fetched": True
                                           }
                                       })
        if match_detail is None:
            return
        match_details_collection.insert_one(match_detail)

    except exceptions.HTTPError:
        print "Server or request error. Match was not parsed, continuing"
        return


def parse_matches():
    global match_id_collection
    pool.map(parse_match, match_id_collection.find({"fetched": False}))
    pool.close()
    pool.join()


# Go through every match_id available on the db
database = db.get_database()
match_id_collection = database.match_ids
match_details_collection = database.match_details
# match_id_collection.update_many({}, {"$set":{"fetched":False}})
parse_matches()
