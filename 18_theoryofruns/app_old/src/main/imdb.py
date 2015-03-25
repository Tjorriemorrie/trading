import logging
from src.main.models import Torrent
from google.appengine.api import mail
from google.appengine.api import urlfetch
import arrow
import re
from bs4 import BeautifulSoup
from pprint import pprint
import Cookie
from time import sleep


class Imdb():
    # urlBase = 'http://www.metacritic.com/search/%s/%s/results?sort=relevancy'
    urlSearch = r'http://www.imdb.com/find?q={0}&&s=tt&ref_=fn_tt_pop'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'
    }
    cookie = None


    def __init__(self):
        urlfetch.set_default_fetch_deadline(60)
        self.cookie = Cookie.SimpleCookie()


    def runMovies(self):
        logging.info('IMDB: movies running...')
        cutoff = arrow.utcnow().replace(days=-3).datetime
        torrents = Torrent.query(Torrent.category_code == 207, Torrent.rating == None, Torrent.uploaded_at > cutoff).fetch()
        logging.info('{0} torrents fetched'.format(len(torrents)))
        results = {}
        for torrent in torrents:
            # find year
            matches = re.match(r'(.*)\(?(19[5-9]\d|20[0-1]\d)', torrent.title)
            if matches is None:
                results[torrent.title] = 'MM%'
                logging.info('No match for {0}'.format(torrent.title.encode('utf-8')))
            else:
                # remove brackets in title
                title = matches.group(1).replace('(', '') + matches.group(2)
                # get imdb search results
                links = self.searchTitle(title.replace(' ', '+'))
                rating, header = self.searchTitleRanking(links)
                if not rating or not header:
                    results[torrent.title] = 'PP%'
                    logging.info('IMDB Title links not found {0}'.format(torrent.title.encode('utf-8')))
                    continue
                logging.info('IMDB Title found {0}'.format(title.encode('utf-8')))

                if r'1080p' in torrent.title.lower():
                    torrent.resolution = 1080
                elif r'720p' in torrent.title.lower():
                    torrent.resolution = 720
                torrent.title_rating = header
                torrent.rating = rating
                torrent.rated_at = arrow.utcnow().datetime.replace(tzinfo=None)
                logging.info('Saved {0}'.format(torrent))
                torrent.put()
                results[torrent.title] = '{0}%'.format(rating)

        self.notify(results)
        logging.info('IMDB: movies ran')


    def searchTitle(self, title):
        logging.info('IMDB title searching {0}'.format(title.encode('utf-8')))
        links = []
        url = self.urlSearch.format(title.encode('utf-8'))
        logging.info('IMDB title url {0}'.format(url))
        res = None
        for i in range(5):
            try:
                res = urlfetch.fetch(url, headers=self.headers)
                cookie = res.headers.get('set-cookie', '')
                self.headers['Cookie'] = cookie
                logging.info('IMDB title cookie {0}'.format(cookie))
                break
            except:
                sleep(i)

        if not res:
            return links

        soup = BeautifulSoup(res.content)
        try:
            rows = soup.find('table', class_='findList').find_all('tr')
            for row in rows:
                links.append(row.find('a')['href'])
        except AttributeError:
            logging.warn('No table or rows in response!')

        logging.info('IMDB title {0} found'.format(len(links)))
        return links


    def searchTitleRanking(self, links):
        for link in links:
            url = 'http://www.imdb.com{0}'.format(link)
            logging.info('IMDB search url {0}'.format(url))
            res = urlfetch.fetch(url, headers=self.headers)

            soup = BeautifulSoup(res.content)
            try:
                rating = soup.find(class_=['star-box', 'giga-star']).find(class_=['titlePageSprite', 'star-box-giga-star']).text.strip()
                header = soup.find('h1', class_='header').find('span', class_='itemprop').text.strip()
                rating = int(float(rating)*10)
                logging.info('IMDB search found rating {0}'.format(rating))
                logging.info('IMDB search found header {0}'.format(header))
                return [rating, header]
            except AttributeError:
                logging.warn('IMDB search: No star box rating for title!')

        return [None, None]


    def notify(self, results):
        mail.send_mail(
            sender='jacoj82@gmail.com',
            to='jacoj82@gmail.com',
            subject="IMDB scraped",
            body='\n'.join(['{0} <= {1}'.format(v, k.encode('utf-8')) for k, v in results.iteritems()]),
        )
