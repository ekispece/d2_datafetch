from string import lower

from d2_db import db

import dryscrape
from bs4 import BeautifulSoup


def extract():
    database = db.get_database()
    heroes_list = database.heroes
    heroes_dyad_collection = database.heroes_dyad
    heroes_matchups_collection = database.matchups

    session = dryscrape.Session()
    session.set_attribute('auto_load_images', False)

    hero_lname_id = {}
    for hero in heroes_list.find():
        hero_lname_id[hero['localized_name']] = hero['id']

    hero_matchups = {}

    for heroes in heroes_list.find():
        hero_url_name = lower(heroes['localized_name']).replace(' ', '-').replace('\'', '')
        matchups_url_name = 'http://www.dotabuff.com/heroes/' + hero_url_name + '/matchups'

        session.visit(matchups_url_name)
        page = session.body()
        soup = BeautifulSoup(page, 'lxml')

        hero_matchups['hero_id'] = heroes['id']
        hero_matchups['matchups'] = {}

        matchups = {}
        for tr in soup.table.tbody.find_all('tr'):
            td = tr.find_all('td')
            matchups[str(hero_lname_id[td[1].text])] = {}
            # assert matchups['id'] is not None
            matchups[str(hero_lname_id[td[1].text])]['advantage'] = float(td[2].text.replace('%', ''))
            matchups[str(hero_lname_id[td[1].text])]['relative_wr'] = float(td[3].text.replace('%', '')) / 100

        hero_matchups['matchups'] = matchups

        print(heroes_matchups_collection.insert(hero_matchups))
        hero_matchups.clear()
