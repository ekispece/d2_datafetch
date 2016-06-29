import operator
import cPickle as pickle
import numpy as np

from d2_db import db

database = db.get_database()
heroes_list_collection = database.heroes
match_details_collection = database.match_details
heroes_metrics_collection = database.heroes_metrics
items_list_collection = database.items_metrics

features_per_hero = 17  # hero_id, agpm, axpm, awr, awmd, akda, ahd, atd, ahh, alh, adn, item123, item123wr
heroes_per_match = 9
total_features = features_per_hero * heroes_per_match

y = []
x = []
m = []

for match in match_details_collection.find():
    winner = match["winner"]
    winners = []
    losers = []
    for player in match["players"]:
        if player["team"] == winner:
            winners.append(player["hero_id"])
        else:
            losers.append(player["hero_id"])
    for hero_id in losers:
        m.append(hero_id)
        h_metric = heroes_metrics_collection.find_one({"hero_id": hero_id})
        h_gpm = float(h_metric["gold"]) / h_metric["games"]
        h_xpm = float(h_metric["xp"]) / h_metric["games"]
        h_wr = float(h_metric["wins"]) / h_metric["games"]
        h_wmd = float(h_metric["won_match_duration"]) / h_metric["games"]
        h_kda = (float((h_metric["kills"] + h_metric["assists"])) / h_metric["deaths"]) / h_metric["games"]
        h_hd = float(h_metric["hero_damage"]) / h_metric["games"]
        h_td = float(h_metric["tower_damage"]) / h_metric["games"]
        h_hh = float(h_metric["hero_healing"]) / h_metric["games"]
        h_lh = float(h_metric["last_hits"]) / h_metric["games"]
        h_den = float(h_metric["denies"]) / h_metric["games"]
        h_i1 = max(h_metric["items"].iteritems(), key=operator.itemgetter(1))[0]
        del h_metric["items"][h_i1]
        h_i2 = max(h_metric["items"].iteritems(), key=operator.itemgetter(1))[0]
        del h_metric["items"][h_i2]
        h_i3 = max(h_metric["items"].iteritems(), key=operator.itemgetter(1))[0]
        del h_metric["items"][h_i3]

        h_i1_ = items_list_collection.find_one({"id": int(h_i1)})
        h_i2_ = items_list_collection.find_one({"id": int(h_i2)})
        h_i3_ = items_list_collection.find_one({"id": int(h_i3)})

        h_i1_wr = float(h_i1_["wins"]) / h_i1_["times_bought"]
        h_i2_wr = float(h_i2_["wins"]) / h_i2_["times_bought"]
        h_i3_wr = float(h_i3_["wins"]) / h_i3_["times_bought"]
        m.extend((h_gpm, h_xpm, h_wr, h_wmd, h_kda, h_hd, h_td, h_hh, h_lh, h_den, int(h_i1), h_i1_wr, int(h_i2),
                  h_i2_wr, int(h_i3), h_i3_wr))

    for del_hero_id in winners:
        y.append(del_hero_id)
        mt = m[:]
        for hero_id in [h for h in winners if h != del_hero_id]:
            mt.append(hero_id)
            h_metric = heroes_metrics_collection.find_one({"hero_id": hero_id})
            h_gpm = float(h_metric["gold"]) / h_metric["games"]
            h_xpm = float(h_metric["xp"]) / h_metric["games"]
            h_wr = float(h_metric["wins"]) / h_metric["games"]
            h_wmd = float(h_metric["won_match_duration"]) / h_metric["games"]
            h_kda = (float((h_metric["kills"] + h_metric["assists"])) / h_metric["deaths"]) / h_metric["games"]
            h_hd = float(h_metric["hero_damage"]) / h_metric["games"]
            h_td = float(h_metric["tower_damage"]) / h_metric["games"]
            h_hh = float(h_metric["hero_healing"]) / h_metric["games"]
            h_lh = float(h_metric["last_hits"]) / h_metric["games"]
            h_den = float(h_metric["denies"]) / h_metric["games"]
            h_i1 = max(h_metric["items"].iteritems(), key=operator.itemgetter(1))[0]
            del h_metric["items"][h_i1]
            h_i2 = max(h_metric["items"].iteritems(), key=operator.itemgetter(1))[0]
            del h_metric["items"][h_i2]
            h_i3 = max(h_metric["items"].iteritems(), key=operator.itemgetter(1))[0]
            del h_metric["items"][h_i3]

            h_i1_ = items_list_collection.find_one({"id": int(h_i1)})
            h_i2_ = items_list_collection.find_one({"id": int(h_i2)})
            h_i3_ = items_list_collection.find_one({"id": int(h_i3)})

            h_i1_wr = float(h_i1_["wins"]) / h_i1_["times_bought"]
            h_i2_wr = float(h_i2_["wins"]) / h_i2_["times_bought"]
            h_i3_wr = float(h_i3_["wins"]) / h_i3_["times_bought"]
            mt.extend((h_gpm, h_xpm, h_wr, h_wmd, h_kda, h_hd, h_td, h_hh, h_lh, h_den, int(h_i1), h_i1_wr, int(h_i2),
                      h_i2_wr, int(h_i3), h_i3_wr))
        x.append(mt)
    m[:] = []

j = np.array(x)

y_out = np.zeros(shape=(j.shape[0], 114))
for y_key, y_val in enumerate(y):
    y_out[y_key][y_val] = 1

np.random.shuffle(j)
np.save("d2_d", j)
np.save("d2_dy", y_out)
