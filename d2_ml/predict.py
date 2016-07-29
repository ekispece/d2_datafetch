from __future__ import print_function
from copy import deepcopy

import numpy as np
import operator

from keras.backend.tensorflow_backend import argmax
from keras.layers import Input, Dense, Activation
from keras.layers.advanced_activations import LeakyReLU
from keras.layers.core import Dropout
from keras.layers.normalization import BatchNormalization
from keras.models import Sequential
from d2_db import db

#
# features_per_hero = 16  # hero_id, agpm, axpm, awr, akda, ahd, atd, ahh, alh, adn, item123, item123wr
# heroes_per_match = 9
total_features = 226
hero_choices = 111

database = db.get_database()
heroes_list_collection = database.heroes
match_details_collection = database.match_details
heroes_metrics_collection = database.heroes_metrics
items_list_collection = database.items_metrics
dyads_list_collection = database.heroes_dyads
hero_matchups_list_collection = database.matchups

heroes_id_dfid_translate = {}
heroes_dfid_id_translate = {}

for hero in heroes_list_collection.find():
    heroes_id_dfid_translate[hero['id']] = hero['id_df']

for hero in heroes_list_collection.find():
    heroes_dfid_id_translate[hero['id_df']] = hero['id']

network = Sequential(
    [
        Dense(2560, input_dim=total_features),
        Dropout(0.25),
        LeakyReLU(alpha=0.4),
        BatchNormalization(epsilon=1e-5, momentum=0.99),
        Dense(2560),
        Dropout(0.2),
        LeakyReLU(alpha=0.3),
        BatchNormalization(epsilon=1e-6),
        Dense(2560),
        Dropout(0.2),
        LeakyReLU(alpha=0.2),
        BatchNormalization(),
        Dense(1000),
        Dropout(0.2),
        LeakyReLU(alpha=0.1),
        BatchNormalization(),
        Dense(1000),
        Dropout(0.2),
        Activation('relu'),
        BatchNormalization(),
        Dense(111),
        Activation('softmax')
    ]
)

network.compile(optimizer='nadam', loss='kld', metrics=['accuracy'])
network.load_weights("model_mlp.d2")

heroes_list = {}
items_list = {}
heroes_name_list = {}
m = []
dyads_list = {}
matchups_list = {}

for hero in heroes_metrics_collection.find():
    heroes_list[hero["hero_id"]] = hero

for hero in heroes_list_collection.find():
    heroes_name_list[hero["id_df"]] = hero["localized_name"]

for item in items_list_collection.find():
    items_list[item["id"]] = item

for hero_dyad in dyads_list_collection.find():
    dyads_list[hero_dyad['hero_id']] = hero_dyad['dyads']

for hero_matchup in hero_matchups_list_collection.find():
    matchups_list[hero_matchup['hero_id']] = hero_matchup['matchups']

winners = [62, 90, 39, 12]
losers = [38, 53, 20, 80, 33]
winner = 'radiant'

for hero_id in losers:
    m.append(heroes_id_dfid_translate[hero_id])
    h_metric = deepcopy(heroes_list[hero_id])
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
    m.extend((h_wmd, h_gpm, h_xpm, h_wr, h_kda, h_hd, h_td, h_hh, h_lh, h_den, int(h_i1), h_i1_wr, int(h_i2),
              h_i2_wr, int(h_i3), h_i3_wr))
    rest_of_team = [x for x in losers if not x == hero_id]
    assert len(rest_of_team) == 4
    # print(hero_id, rest_of_team)
    dyads_ = [(float(dyads_list[hero_id].get(str(x), dict()).get('wins', 0)) / dyads_list[hero_id].get(str(x), dict())
               .get('matches', 1)) for x in rest_of_team]
    m.extend(dyads_)

for hero_id in winners:
    m.append(heroes_id_dfid_translate[hero_id])
    h_metric = deepcopy(heroes_list[hero_id])
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
    m.extend((h_wmd, h_gpm, h_xpm, h_wr, h_kda, h_hd, h_td, h_hh, h_lh, h_den, int(h_i1), h_i1_wr,
              int(h_i2), h_i2_wr, int(h_i3), h_i3_wr))
    rest_of_team = [x for x in winners if not x == hero_id]
    assert len(rest_of_team) == 3
    dyads_ = [(float(dyads_list[hero_id].get(str(x), dict()).get('wins', 0)) / dyads_list[hero_id].get(str(x), dict())
               .get('matches', 1)) for x in rest_of_team]
    m.extend(dyads_)

    matchups_ = [
        [matchups_list[hero_id][str(x)]['relative_wr'], matchups_list[hero_id][str(x)]['advantage']]
        for x in losers]
    # reducing list of lists to a single list
    matchups_ = [i for sl in matchups_ for i in sl]

    m.extend(matchups_)

m.append(1 if winner == 'radiant' else -1)
x_in = np.zeros(shape=(1, len(m)))
x_in[0] = m
# print "correct: " + str(del_hero_id)
c_out = network.predict(x_in)
choices = np.argpartition(c_out[0], -hero_choices)[-hero_choices:]

print(("*" * 10) + "\ntheir team: ")
for h in losers:
    print(heroes_name_list[heroes_id_dfid_translate[h]], end=", ")

print("\n\n" + ("*" * 10) + "\nyour team: ")
for h in winners:
    print(heroes_name_list[heroes_id_dfid_translate[h]], end=", ")

print("\n\n")
print("you should probably pick:")

final_choices = []

for i in choices:
    # if i in losers:
    #     continue
    # if i in winners:
    #     continue
    final_choices.append((c_out[0][i], heroes_name_list[i]))
    # print('i: ', i)

for prob, hero in sorted(final_choices, reverse=True):
    print(hero, ' :\t', str(prob * 100) + '%')

# print(network.predict_classes(x_in))