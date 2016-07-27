from __future__ import print_function
import operator
import cPickle as pickle
import numpy as np
from copy import deepcopy

import datetime

from d2_db import db


# TODO: refactor this to not use too much memory
def prepare_data():
    database = db.get_database()
    heroes_list_collection = database.heroes
    match_details_collection = database.match_details
    heroes_metrics_collection = database.heroes_metrics
    items_list_collection = database.items_metrics

    features_per_hero = 16  # hero_id, agpm, axpm, awr, akda, ahd, atd, ahh, alh, adn, item123, item123wr
    heroes_per_match = 9
    total_features = features_per_hero * heroes_per_match

    heroes_list = {}
    items_list = {}
    m = []
    heroes_id_dfid_translate = {}

    for hero in heroes_list_collection.find():
        heroes_id_dfid_translate[hero['id']] = hero['id_df']

    for hero in heroes_metrics_collection.find():
        heroes_list[hero["hero_id"]] = hero

    for item in items_list_collection.find():
        items_list[item["id"]] = item

    print(items_list)

    total_matches = match_details_collection.count()
    total_sint_matches = total_matches * 5

    x = np.zeros(shape=(total_sint_matches, total_features + 1))  # label included
    processed_matches = 0
    feature_num = 0

    start_time = datetime.datetime.now().replace(microsecond=0)

    for match in match_details_collection.find():
        processed_matches += 1

        if processed_matches % 1000 == 0:
            end_time = datetime.datetime.now().replace(microsecond=0)
            print("Processed " + str(processed_matches) + " out of " + str(total_matches) + " Time taken : " + str(
                end_time - start_time))
            start_time = end_time

        winner = match["winner"]
        winners = []
        losers = []
        for player in match["players"]:
            if player["team"] == winner:
                winners.append(player["hero_id"])
            else:
                losers.append(player["hero_id"])
        for hero_id in losers:
            m.append(heroes_id_dfid_translate[hero_id])
            h_metric = deepcopy(heroes_list[hero_id])
            h_gpm = float(h_metric["gold"]) / h_metric["games"]
            h_xpm = float(h_metric["xp"]) / h_metric["games"]
            h_wr = float(h_metric["wins"]) / h_metric["games"]
            # h_wmd = float(h_metric["won_match_duration"]) / h_metric["games"]
            h_kda = float((h_metric["kills"] + h_metric["assists"])) / h_metric["deaths"]
            h_hd = float(h_metric["hero_damage"]) / h_metric["games"]
            h_td = float(h_metric["tower_damage"]) / h_metric["games"]
            h_hh = float(h_metric["hero_healing"]) / h_metric["games"]
            h_lh = float(h_metric["last_hits"]) / h_metric["games"]
            h_den = float(h_metric["denies"]) / h_metric["games"]
            h_i1 = max(h_metric["items"].items(), key=operator.itemgetter(1))[0]
            del h_metric["items"][h_i1]
            h_i2 = max(h_metric["items"].items(), key=operator.itemgetter(1))[0]
            del h_metric["items"][h_i2]
            h_i3 = max(h_metric["items"].items(), key=operator.itemgetter(1))[0]
            del h_metric["items"][h_i3]

            h_i1_ = items_list[int(h_i1)]
            h_i2_ = items_list[int(h_i2)]
            h_i3_ = items_list[int(h_i3)]

            h_i1_wr = float(h_i1_["wins"]) / h_i1_["times_bought"]
            h_i2_wr = float(h_i2_["wins"]) / h_i2_["times_bought"]
            h_i3_wr = float(h_i3_["wins"]) / h_i3_["times_bought"]
            m.extend((h_gpm, h_xpm, h_wr, h_kda, h_hd, h_td, h_hh, h_lh, h_den, int(h_i1), h_i1_wr, int(h_i2),
                      h_i2_wr, int(h_i3), h_i3_wr))

        for del_hero_id in winners:
            mt = m[:]
            for hero_id in [h for h in winners if h != del_hero_id]:
                mt.append(heroes_id_dfid_translate[hero_id])
                h_metric = deepcopy(heroes_list[hero_id])
                h_gpm = float(h_metric["gold"]) / h_metric["games"]
                h_xpm = float(h_metric["xp"]) / h_metric["games"]
                h_wr = float(h_metric["wins"]) / h_metric["games"]
                # h_wmd = float(h_metric["won_match_duration"]) / h_metric["games"]
                h_kda = float((h_metric["kills"] + h_metric["assists"])) / h_metric["deaths"]
                h_hd = float(h_metric["hero_damage"]) / h_metric["games"]
                h_td = float(h_metric["tower_damage"]) / h_metric["games"]
                h_hh = float(h_metric["hero_healing"]) / h_metric["games"]
                h_lh = float(h_metric["last_hits"]) / h_metric["games"]
                h_den = float(h_metric["denies"]) / h_metric["games"]
                h_i1 = max(h_metric["items"].items(), key=operator.itemgetter(1))[0]
                del h_metric["items"][h_i1]
                h_i2 = max(h_metric["items"].items(), key=operator.itemgetter(1))[0]
                del h_metric["items"][h_i2]
                h_i3 = max(h_metric["items"].items(), key=operator.itemgetter(1))[0]
                del h_metric["items"][h_i3]

                h_i1_ = items_list[int(h_i1)]
                h_i2_ = items_list[int(h_i2)]
                h_i3_ = items_list[int(h_i3)]

                h_i1_wr = float(h_i1_["wins"]) / h_i1_["times_bought"]
                h_i2_wr = float(h_i2_["wins"]) / h_i2_["times_bought"]
                h_i3_wr = float(h_i3_["wins"]) / h_i3_["times_bought"]
                mt.extend((h_gpm, h_xpm, h_wr, h_kda, h_hd, h_td, h_hh, h_lh, h_den, int(h_i1), h_i1_wr, int(h_i2),
                           h_i2_wr, int(h_i3), h_i3_wr))
            mt.append(heroes_id_dfid_translate[del_hero_id])
            x[feature_num] = mt
            feature_num += 1
        m[:] = []

    np.random.shuffle(x)
    np.save("d2_d", x)
