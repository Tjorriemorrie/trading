import logging
from google.appengine.api import mail
from src.main.models import Torrent, UserTorrent
# import requests
from bs4 import BeautifulSoup
from pprint import pprint
import arrow


class Kickass():

    URL_BASE = 'http://kickass.so'
    CATEGORIES = [
        'highres-movies',
        'tv',
        'pc-games',
    ]


    def scrape(self):
        for category in self.CATEGORIES:
            logging.info('kickass cat {0}'.format(category))
            # get list of torrents per page
            pages = 10 if category == 'tv' else (6 if category == 'highres-movies' else 3)
            for p in xrange(1, pages+1):
                logging.info('kickass p {0}'.format(p))
                list = self.scrapeList(category, p)
                self.saveList(list)


    def scrapeList(self, category, p):
        logging.info('Kickass scraping {0} page {1}'.format(category, p))
        res = requests.get('{0}/{1}/{2}/'.format(self.URL_BASE, category, p), timeout=59)
        res.raise_for_status()
        soup = BeautifulSoup(res.content)
        table = soup.find('table', class_='data')
        list = []
        for tr in table.find_all('tr')[2:]:
            item = {}
            link = tr.find('a', class_='cellMainLink')
            item['url'] = link['href']
            item['title'] = link.text
            item['uploader'] = tr.find('div', class_='torrentname').span.a.text
            item['magnet'] = tr.find('a', class_='imagnet')['href']
            item['size'] = tr.find_all('td')[1].text
            item['files'] = tr.find_all('td')[2].text
            item['seeders'] = int(tr.find_all('td')[4].text)
            item['leechers'] = int(tr.find_all('td')[5].text)
            item['category'] = category
            value, scale = tr.find_all('td')[3].text.strip().split()
            scale += 's' if scale[-1] != 's' else ''
            params = {scale:-int(value)}
            # logging.info('scale = {0}'.format(params))
            uploaded_at = arrow.utcnow().replace(**params)
            item['uploaded_at'] = uploaded_at.datetime.replace(tzinfo=None)
            # pprint(item)
            list.append(item)
        logging.info('Kickass scraped {0} page {1} found {2}'.format(category, p, len(list)))
        return list


    def saveList(self, list):
        logging.info('list: saving...')
        for item in list:
            torrent = Torrent.query(Torrent.url == item['url']).get()
            if not torrent:
                torrent = Torrent(**item)
            torrent.populate(**item)
            torrent.put()
            logging.info('list: saved {0}'.format(torrent))
        logging.info('list: saved')


    def clean(self):
        logging.info('Kickass: cleaning...')
        results = []

        # cleaning old torrents
        cutoff = arrow.utcnow().replace(days=-7).datetime
        torrents = Torrent.query(Torrent.updated_at < cutoff).order(Torrent.updated_at).fetch()
        logging.info('{0} torrents found that is older than {1}'.format(len(torrents), cutoff))
        for torrent in torrents:
            results.append(torrent.title)
            torrent.key.delete()
            logging.info('Deleted T {0}'.format(torrent.title.encode('utf-8')))

        # cleaning invalid user torrents
        uts = UserTorrent.query().fetch()
        logging.info('{0} usertorrents found that is invalid'.format(len(uts)))
        for ut in uts:
            if not ut.get_torrent():
                results.append(str(ut.key.id()))
                ut.key.delete()
                logging.info('Deleted UT {0}'.format(ut.key.id()))

        mail.send_mail(
            sender='jacoj82@gmail.com',
            to='jacoj82@gmail.com',
            subject="Torrents cleaned",
            body='\n'.join(results),
        )
        logging.info('Kickass: cleaned')