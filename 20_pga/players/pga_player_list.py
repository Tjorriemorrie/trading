import logging as log
import requests
from bs4 import BeautifulSoup
from bs4.diagnose import diagnose
from pprint import pprint
from pyquery import PyQuery as pq
from lxml import etree
import os
import pickle
import re
from argparse import ArgumentParser


class PgaPlayerList():
    url_base = 'http://www.pgatour.com/players.html'
    re_player_id = re.compile('\.(\d+)\.')

    def run(self):
        log.info('run start')

        self.scrapePlayerList()

        log.info('run end')


    def scrapePlayerList(self):
        log.debug('url: {}'.format(self.url_base))
        res = requests.get(self.url_base)
        res.raise_for_status()

        # parse html
        html = BeautifulSoup(res.content)
        options = html.select('.directory-select option')
        log.info('{} total rows'.format(len(options)))
        data = {}
        for option in options[1:]:
            # print(option.prettify())
            player_name = option.text.replace(u'\xa0', u' ')
            player_id = self.re_player_id.search(option['value']).group(1)
            data[player_name] = player_id
        # pprint(data[:5])

        # save
        file = '{}/_list.pkl'.format(os.path.dirname(os.path.realpath(__file__)))
        if not os.path.exists(os.path.dirname(file)):
            os.makedirs(os.path.dirname(file))
        with open(file, 'w') as f:
            pickle.dump(data, f)


if __name__ == '__main__':
    log.basicConfig(
        level=log.DEBUG,
        format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s',
        # datefmt='%Y-%m-%d %H:%M:',
    )

    pga_player_list = PgaPlayerList()
    pga_player_list.run()
