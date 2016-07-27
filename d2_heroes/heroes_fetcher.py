#!/usr/bin/python
from dota2py import api as dota_api
from d2_db import db


def cmp_hero_name(h1, h2):
    if h1['localized_name'] < h2['localized_name']:
        return -1
    return 1


class HeroesFetcher:
    def __init__(self):
        dota_api.set_api_key("3A315E5FE932409684A1C2DB288A92C6")  # When possible do substitute this key by your own

    def get_heroes_info(self):
        return self.heroes_tuple(dota_api.get_heroes())

    @staticmethod
    def heroes_tuple(json):
        return json["result"]["heroes"]

    def extract_hero_info(self, hero_info):
        return hero_info["localized_name"], hero_info["name"], hero_info["id"]


def fetch():
    data = db.get_database()

    if "heroes" in data.collection_names():
        print("Heroes are already fetched")
    else:
        heroes = HeroesFetcher()
        heroes_info = heroes.get_heroes_info()
        for ix, hero_info in enumerate(sorted(heroes_info, cmp=cmp_hero_name)):
            hero_info['id_df'] = ix

        data.heroes.insert_many(heroes_info)
