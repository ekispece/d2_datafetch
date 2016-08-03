#!/usr/bin/python
from collections import Counter

from d2_db import db


# Can also be used to calculate matchups
# Reason why it's not used to calculate matchups is that we're using dotabuff's advantage metric
def calculate_dyads():
    database = db.get_database()
    heroes_collection = database.heroes
    matches_collection = database.match_details
    dyads_collection = database.heroes_dyads
    heroes_dyads = {}
    heroes_dyads_list = []

    total_matches = matches_collection.count()
    matches = 0

    for hero in heroes_collection.find():
        heroes_dyads[hero['id']] = {
            'hero_id': hero['id'],
            'wins': Counter(),
            'matches': Counter()
        }

    for match in matches_collection.find():
        matches += 1
        if matches % 1000 == 0:
            print('Parsed ', matches, 'matches out of ', total_matches)
        winner = match['winner']
        players = match['players']
        assert len(players) == 10
        for player in players:
            his_team = [x for x in players if not x == player and x['team'] == player['team']]
            assert len(his_team) == 4
            if player['team'] == winner:
                heroes_dyads[player['hero_id']]['wins'].update([x['hero_id'] for x in his_team])
            heroes_dyads[player['hero_id']]['matches'].update([x['hero_id'] for x in his_team])

    for hero in heroes_collection.find():
        hd = {
            'hero_id': hero['id'],
            'dyads': {}
        }
        for key, val in heroes_dyads[hero['id']]['matches'].items():
            hd['dyads'][str(key)] = {
                'matches': val,
                'wins': heroes_dyads[hero['id']]['wins'].get(key, 0)
            }
        heroes_dyads_list.append(hd)

    assert len(heroes_dyads_list) == 111

    dyads_collection.insert_many(heroes_dyads_list)
