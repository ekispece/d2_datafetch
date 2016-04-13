from d2_db import db

match_details = db.get_database().match_details

print match_details.remove({"players.team": None})
