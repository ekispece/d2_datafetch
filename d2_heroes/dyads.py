#!/usr/bin/python
from d2_db import db


# Can also be used to calculate matchups
# Reason why it's not used to calculate matchups is that we're using dotabuff's advantage metric
def calculate_dyads():
    print('i\'m here')
    raw_input()
    database = db.get_database()
    heroes_collection = database.heroes
    matches_collection = database.match_details

    hero_dyad = {}

    for hero in heroes_collection.find():
        hero_dyad['hero_id'] = hero['id']
        hero_dyad['dyads'] = {}
        for match in matches_collection.find({'players.hero_id': hero['id']}):
            winner = match['winner']
            this_hero_team = [h for h in match['players'] if h['hero_id'] == hero['id']][0]['team']

            win = 0
            if this_hero_team == winner:
                win = 1

            other_heroes = [h for h in match['players'] if
                            not h['hero_id'] == hero['id'] and h['team'] == this_hero_team]
            assert len(other_heroes) == 4
            for hero_id in [x['hero_id'] for x in other_heroes]:
                if hero_dyad['dyads'].get(str(hero_id)) is None:
                    hero_dyad['dyads'][str(hero_id)] = {'matches': 0, 'wins': 0}
                hero_dyad['dyads'][str(hero_id)]['matches'] += 1
                hero_dyad['dyads'][str(hero_id)]['wins'] += win

        database.heroes_dyads.insert(hero_dyad)

        hero_dyad.clear()
