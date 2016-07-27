from string import lower

from d2_db import db

import dryscrape
from bs4 import BeautifulSoup

# This might be useless, not using as of yet
database = db.get_database()
heroes_dyad_collection = database.heroes_tryad


session = dryscrape.Session()

session.visit('https://yasp.co/picks/3')
page = session.body()

soup = BeautifulSoup(page, 'lxml')
dyad_list = []

for dyad in soup.find(id='picks').find('tbody').find_all('tr'):
    dyad_obj = {}
    heroes = dyad.find('td', class_='text-left').find_all('span')[2].string.split(' / ')
    wr = float(dyad.find_all('div', class_='rankable')[4].string.replace('%', ''))
    dyad_obj['win_rate'] = wr
    dyad_obj['heroes'] = (heroes[0], heroes[1], heroes[2])
    print(dyad_obj)
    dyad_list.append(dyad_obj)


heroes_dyad_collection.insert_many(dyad_list)
