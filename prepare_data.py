#!/usr/bin/python
# Including python3 support
from __future__ import print_function

from logging import warning

import aggregate_metrics_items as ami
import aggregate_metrics_heroes as amh
from d2_db import db
from d2_items import items_fetcher as ift
from d2_heroes import heroes_fetcher as hf
from d2_ml import load_input_data as idata

database = db.get_database()
heroes_collection = database.heroes
heroes_metrics_collection = database.heroes_metrics
items_collection = database.items
items_metrics_collection = database.items_metrics

print('Checking heroes collection consistency')
if heroes_collection.count() == 0:
    hf.fetch()

# asserting we have the correct number of heroes in the db
print('Heroes collection mounted, checking whether there\'s 111 heroes')
assert heroes_collection.count() == 111
print('ok')

print('Checking items collection consistency')
if items_collection.count() == 0:
    ift.fetch()

print('Items collection mounted, checking whether there\'s all items in it')
# This might change from time to time, since new items are added consistently
assert items_collection.count() == 281
print('ok')

print('It\'s not in the scope of this file to parse matches. Please make sure all of them are available at this point')
print('There\'s a total of', database.match_ids.count(), 'match id\'s in db. Which yielded a total of',
      database.match_details.count(), 'matches parsed so far.')
warning('make sure the number above is correct')

print('aggregating metrics for items')
items_metrics_collection.drop()
ami.start()
print('ok')

print('aggregating metrics for heroes')
heroes_metrics_collection.drop()
amh.start()
print('checking heroes metrics consistency')
assert heroes_metrics_collection.count() == heroes_collection.count()
print('ok')

print('You may grab a cup of coffee now, preparing the whole data into a big file. This can take up a loooong time')
idata.prepare_data()
print('We survived')
print('Everything seems ok. Ready to train')
