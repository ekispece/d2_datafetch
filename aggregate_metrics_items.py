from d2_db import db
from d2_items.useless_items_list import get_useless_items_list


def start():
    database = db.get_database()
    items_list_collection = database.items
    match_details_collection = database.match_details
    items_metrics_collection = database.items_metrics

    items_list = []
    for item in items_list_collection.find():  # this creates the collection in case it doesn't exists
        if item["id"] not in get_useless_items_list():
            if items_metrics_collection.find_one({"id": item["id"]}) is None:
                items_metrics_collection.insert_one(
                    {
                        "id": item["id"],
                        "times_bought": 0,
                        "wins": 0,
                    }
                )

    for a_match in match_details_collection.find():
        winner_label = a_match["winner"]
        for player in a_match["players"]:
            if "team" not in player:
                print "match not found"
                print a_match
                match_details_collection.remove({'_id': a_match['_id']})
                continue
            is_win = (winner_label == player["team"])
            bought_items = []
            for item in player["items"]:
                if item["item_id"] not in bought_items:
                    bought_items.append(item["item_id"])
            for item_id in bought_items:
                win_count = 1 if is_win else 0
                items_metrics_collection.update_one({"id": item_id},
                                                    {
                                                        "$inc": {
                                                            "times_bought": 1,
                                                            "wins": win_count
                                                        }
                                                    })

                # pool.map(parse_item_metrics, match_details_collection.find())
