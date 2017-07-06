#!/usr/bin/python
from dota2py import api as dota_api
from dota2py.api import json_request_response

from d2_db import db


class ItemsFetcher:
    def __init__(self):
        dota_api.set_api_key("")  # When possible do substitute this key by your own

    def get_items_info(self):
        return self.items_tuple(self.get_items())

    @json_request_response
    def get_items(self, **kwargs):
        """
        Get a list of hero identifiers
        """
        return dota_api.make_request("GetGameItems",
                                     base="http://api.steampowered.com/IEconDOTA2_570/", **kwargs)

    @staticmethod
    def items_tuple(json):
        return json["result"]["items"]

    @staticmethod
    def extract_item_info(hero_info):
        return hero_info["localized_name"], hero_info["name"], hero_info["id"]


def fetch():
    data = db.get_database()

    if "items" in data.collection_names():
        print("Items are already fetched")
    else:
        items = ItemsFetcher()
        items_info = items.get_items_info()

        data.items.insert_many(items_info)
