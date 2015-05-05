import logging as log
import requests
from bs4 import BeautifulSoup
from bs4.diagnose import diagnose
from pprint import pprint
from lxml import etree
import os
import pickle
import re
from argparse import ArgumentParser
import time


class PgaTourney():
    tourney = '20150505_tpc_sawgrass'
    url_past = 'http://www.pgatour.com/content/pgatour/tournaments/the-players-championship/past-results/jcr:content/mainParsys/pastresults.selectedYear.{}.html'
    url_current = 'http://www.pgatour.com/data/r/011/leaderboard-v2.json?ts={}'.format(int(time.time() * 1000))
    url_stats = 'http://www.pgatour.com/data/players/{0}/{1}stat.json'
    url_betting = 'http:'
    file_player_list = '{}/players/_list.pkl'.format(os.path.dirname(os.path.realpath(__file__)))
    year_start = 2000
    year_current = 2015
    player_ids_past = {}
    player_ids_current = []

    def __init__(self):
        # first get player ids from player names
        with open(self.file_player_list, 'r') as f:
            self.players = pickle.load(f)


    def run(self):
        log.info('run start')

        # get past results
        for year in range(self.year_start, self.year_current):
            log.info('=' * 30)
            log.info(year)
            log.info('=' * 30)
            self.scrapeListPast(year)

        # get this year's leaderboard
        self.scrapeListCurrent()

        # get players' stats
        self.scrapePlayerStats()

        # rest is in notebook
        log.info('run end')


    def scrapeListPast(self, year):
        self.player_ids_past[year] = []
        url = self.url_past.format(year)
        log.debug('url: {}'.format(url))
        res = requests.get(url)
        res.raise_for_status()

        # parse html
        html = BeautifulSoup(res.content)
        rows = html.select('.table-styled tr')
        log.info('{} total rows'.format(len(rows)))
        data = []
        for row in rows[3:]:
            # print(row.prettify())
            cols = row.find_all('td')
            # log.info('{} total cols'.format(len(cols)))
            player_name = cols[0].text.strip()
            player_id = self.players[player_name] if player_name in self.players else None
            if not player_id:
                log.error('Player not found: {}'.format(player_name))
                continue
            else:
                log.info('Player {} <= {}'.format(player_id, player_name))
                self.player_ids_past[year].append(player_id)

            try:
                data.append({
                    'player_name': player_name,
                    'player_id': player_id,
                    'pos': cols[1].text.strip(),
                    'r1': int(cols[2].text.strip()) if cols[2].text else None,
                    'r2': int(cols[3].text.strip()) if cols[3].text else None,
                    'r3': int(cols[4].text.strip()) if cols[4].text else None,
                    'r4': int(cols[5].text.strip()) if cols[5].text else None,
                    'score': int(cols[6].text.strip()),
                    'money': float(cols[7].text.replace('$', '').replace(',', '').strip()) if cols[7].text else 0.,
                    'points': float(cols[8].text.replace(',', '').strip()) if cols[8].text else 0.,
                })
            except Exception as e:
                log.error(e.message)
        # pprint(data[:5])

        # save
        file = '{}/{}/{}.pkl'.format(os.path.dirname(os.path.realpath(__file__)), self.tourney, year)
        if not os.path.exists(os.path.dirname(file)):
            os.makedirs(os.path.dirname(file))
        with open(file, 'w') as f:
            pickle.dump(data, f)


    def scrapeListCurrent(self):
        log.info('scrape tourney current')
        while True:
            try:
                log.debug('url: {}'.format(self.url_current))
                res = requests.get(self.url_current)
                res.raise_for_status()
                break
                # pprint(res.text)
            except Exception as e:
                log.error(e.message)
                pass

        res = res.json()
        players = res['leaderboard']['players']
        log.info('{} players found'.format(len(players)))
        # pprint(players[0])
        data = []
        for player in players:
            # print player
            name = '{} {}'.format(player['player_bio']['first_name'], player['player_bio']['last_name'])
            log.info('Player {} <= {}'.format(name, player['player_id']))
            data.append(player['player_id'])
        # pprint(data[:5])
        self.player_ids_current = data

        # save
        file = '{}/{}/{}.pkl'.format(os.path.dirname(os.path.realpath(__file__)), self.tourney, self.year_current)
        if not os.path.exists(os.path.dirname(file)):
            os.makedirs(os.path.dirname(file))
        with open(file, 'w') as f:
            pickle.dump(data, f)
        log.info('scrape tourney current')


    def scrapePlayerStats(self):
        log.info('scrape player stats')

        # past results
        # pprint(self.player_ids_current)
        for year, player_ids in self.player_ids_past.iteritems():
            log.info('=' * 30)
            log.info(year)
            log.info('=' * 30)
            for player_id in player_ids:
                self.scrapePlayer(player_id, year)

        # current results
        log.info('=' * 30)
        log.info(self.year_current)
        log.info('=' * 30)
        for player_id in self.player_ids_current:
            self.scrapePlayer(player_id, self.year_current)

        log.info('scrape player stats')


    def scrapePlayer(self, player_id, year):
        log.info('scrape player {}'.format(year))
        log.info('scrape player {}'.format(player_id))
        file = '{}/players/{}/{}.pkl'.format(os.path.dirname(os.path.realpath(__file__)), year, player_id)
        if os.path.isfile(file):
            log.info('scrape player file exists')
            return

        # update
        res = None
        for _ in range(3):
            try:
                url = self.url_stats.format(player_id, year)
                log.debug('url: {}'.format(url))
                res = requests.get(url)
                res.raise_for_status()
                res = res.json()
                break
                # pprint(res)
            except Exception as e:
                log.error(e.message)
                time.sleep(5)
        if not res:
            return

        try:
            player_info = res['plrs'][0]
            player_name = player_info['plrName']
            statCats = player_info['years'][0]['tours'][0]['statCats']
            log.info('scrape player {}'.format(player_name))
        except IndexError as e:
            log.error('{}'.format(e.message))
            time.sleep(5)
            return

        data = {}
        for statCat in statCats:
            prefix = statCat['catName']
            for stat in statCat['stats']:
                key = '{}_{}'.format(prefix, stat['name'].replace(' ', '_')).lower()
                val = self.clean(stat['value'])
                data[key] = val
        # pprint(data)
        log.info('scrape player {} stats found'.format(len(data)))

        # save
        if not os.path.exists(os.path.dirname(file)):
            os.makedirs(os.path.dirname(file))
        with open(file, 'w') as f:
            pickle.dump(data, f)
        time.sleep(1)


    def clean(self, val):
        # print val
        if not val:
            return None

        # percentage
        if '%' in val:
            val = float(val.strip('%')) / 100

        # distance
        elif '"' in val:
            # print val
            units = val.strip().split(' ')
            if len(units) == 2:
                val = (int(units[0][:-1]) + (int(units[1][:-1]) / 12)) / 3.25
            else:
                val = int(units[0][:-1]) / 3.25

        # amount
        elif '$' in val:
            val = val.replace('$', '').replace(',', '')

        if not isinstance(val, float):
            val = float(val.replace(',', ''))

        return val

if __name__ == '__main__':
    log.basicConfig(
        level=log.DEBUG,
        format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s',
        # datefmt='%Y-%m-%d %H:%M:',
    )

    pga_tourney = PgaTourney()
    pga_tourney.run()
