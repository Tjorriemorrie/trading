import logging
from google.appengine.ext import ndb
import urllib2
from bs4 import BeautifulSoup
from google.appengine.api import urlfetch
from datetime import datetime, timedelta
from src.main.models import Torrent
from time import sleep


class PirateBay():

    GROUPS = [
        {'code': 100, 'name': 'Audio', 'categories': [
            {'code': 101, 'name': 'Music', 'pages': 2},
            {'code': 102, 'name': 'AudioBooks', 'pages': 2},
        ]},
        {'code': 600, 'name': 'Other', 'categories': [
            {'code': 601, 'name': 'eBooks', 'pages': 2},
        ]},
        {'code': 300, 'name': 'Applications', 'categories': [
            {'code': 301, 'name': 'Windows', 'pages': 2},
            # {'code': 302, 'name': 'Mac', 'pages': 1},
        ]},
        {'code': 400, 'name': 'Games', 'categories': [
            {'code': 401, 'name': 'PC Games', 'pages': 2},
        ]},
        {'code': 200, 'name': 'Video', 'categories': [
            {'code': 209, 'name': '3D', 'pages': 2},
            {'code': 207, 'name': 'HD Movies', 'pages': 5},
            {'code': 205, 'name': 'TV Shows', 'pages': 10},
        ]},
    ]


    def __init__(self):
        logging.info('PirateBay: init: started')
        urlfetch.set_default_fetch_deadline(60)


    def scrape(self):
        logging.info('PirateBay: scrape: started')
        for group in self.GROUPS:
            logging.info('PirateBay: scrape: Group = {0}'.format(len(group)))
            for category in group['categories']:
                logging.info('PirateBay: scrape: Category = {0}'.format(len(category)))
                for p in range(category['pages']):
                    logging.info('PirateBay: scrape: Page = {0}'.format(p))
                    self.scrapePage(group, category, p)

        logging.info('PirateBay: scrape: ended')


    def scrapePage(self, group, category, p):
        logging.info('PirateBay: scrapePage: {0} {1} {2}'.format(group['name'], category['name'], p))

        item = {
            'group_code': group['code'],
            'group_name': group['name'],
            'category_code': category['code'],
            'category_name': category['name'],
        }

        # 3 tries to scrape page
        rows = None
        for n in xrange(3):
            try:
                url = 'http://thepiratebay.se/browse/{0}/{1}/7/0'.format(category['code'], p)
                logging.info('PirateBay: scrapePage: url {0}'.format(url))
                res = urlfetch.fetch(url)
                # logging.info('res {0}'.format(res.content))

                html = BeautifulSoup(res.content)
                rows = html.find('table', id='searchResult').find_all('tr')[1:-1]
                break
            except:
                logging.error('Could not scrape with try {0}'.format(n))
                sleep(1)

        if rows:
            for row in rows:
                # logging.info('row html {0}'.format(row))
                row_top = row.find('div', class_='detName')
                # title
                item['title'] = row_top.find('a').text
                # url
                item['url'] = row_top.find('a')['href']
                # magnet
                item['magnet'] = row.find('a', title='Download this torrent using magnet')['href']

                details = row.find('font', class_='detDesc').text
                details_date, details_size, details_uploader = details.split(',')

                # date
                details_date_val = details_date.split(' ', 1)[1].replace(u"\xa0", u" ")
                if 'Y-day' in details_date_val:
                    details_datetime = datetime.utcnow().replace(hour=int(details_date_val[-5:-3]), minute=int(details_date_val[-2:])) + timedelta(days=-1)
                elif 'Today' in details_date_val:
                    details_datetime = datetime.utcnow().replace(hour=int(details_date_val[-5:-3]), minute=int(details_date_val[-2:]))
                elif 'mins ago' in details_date_val:
                    details_datetime = datetime.utcnow().replace(minute=int(details_date_val.split(' ')[0]))
                elif ':' in details_date:
                    details_datetime = datetime.strptime(details_date_val, '%m-%d %H:%M')
                    details_datetime = details_datetime.replace(year=datetime.utcnow().year)
                else:
                    details_datetime = datetime.strptime(details_date_val, '%m-%d %Y')
                item['uploaded_at'] = details_datetime.replace(tzinfo=None)
                # logging.info('Date extracted {0} from {1}'.format(item['uploaded_at'], details_date.encode('utf-8')))

                # size
                details_size_split = details_size.replace(u"\xa0", u" ").strip().split(' ')
                details_size_mul = 9 if 'GiB' in details_size_split[2] else (6 if 'MiB' in details_size_split[2] else 3)
                item['size'] = int((float(details_size_split[1])) * 10**details_size_mul)

                # uploader
                item['uploader'] = details_uploader.split(' ')[-1]

                # seeders
                item['seeders'] = int(row.find_all('td')[2].text)
                # leechers
                item['leechers'] = int(row.find_all('td')[3].text)

                # logging.info('item {0}'.format(item))

                # save
                url_split = item['url'].split('/')
                item_key = ndb.Key('Torrent', url_split[2])
                torrent = item_key.get()
                if not torrent:
                    torrent = Torrent(key=item_key)
                torrent.populate(**item)
                torrent.put()
                logging.info('Torrent {0}'.format(torrent))





# DETAILED PAGE
# item = {
# 'tpb_id': link['href'].split('/')[2],
# }
# # print '<p>link = ' + link['href'] + '</p>'
# resultDetail = self.scrapeDetail(self.urlBase + link['href'])
# det = BeautifulSoup(resultDetail)
# # print det.prettify().encode('utf8')
# # requireds
# try:
# item['title'] = det.find('div', id='title').text.strip()
# item['files'] = det.find('dt', text=re.compile('Files:')).findNext('dd').text.strip()
# item['size'] = self.patternSize.match(det.find('dt', text=re.compile('Size:')).findNext('dd').text).group(1)
# item['uploaded_at'] = datetime.datetime.strptime(det.find('dt', text=re.compile('Uploaded:')).findNext('dd').text.strip(), '%Y-%m-%d %H:%M:%S %Z')
# item['user'] = det.find('dt', text=re.compile('By:')).findNext('dd').text.strip()
# item['seeders'] = det.find('dt', text=re.compile('Seeders:')).findNext('dd').text.strip()
# item['leechers'] = det.find('dt', text=re.compile('Leechers:')).findNext('dd').text.strip()
# item['magnet'] = det.find_all('a', title='Get this torrent')[0]['href']
# item['nfo'] = det.find_all('div', class_='nfo')[0].text.strip()
# except AttributeError:
# logging.warn('No title for {0}'.format(link['href']))
# continue
# # optionals
# if det.find('div', class_='torpicture'):
# item['img'] = 'http:' + det.find_all('img', title='picture')[0]['src']
# else:
# item['img'] = 'http://www.thepiratebay.se/static/img/tpblogo_sm_ny.gif'
# self.saveData([item], category)
# # print 'item'
# # print item
# # break
#
