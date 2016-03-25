#!/usr/bin/python
from dota2py import api as dota_api
from d2_db import db


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

data = db.get_database()

if "heroes" in data.collection_names():
    print("Heroes are already fetched")
else:
    heroes = HeroesFetcher()
    heroes_info = heroes.get_heroes_info()

    data.heroes.insert_many(heroes_info)
