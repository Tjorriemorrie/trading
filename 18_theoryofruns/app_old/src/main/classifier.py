import logging
from src.main.models import Torrent
import requests
from bs4 import BeautifulSoup
from pprint import pprint


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
            for p in xrange(1, 5):
                logging.info('kickass p {0}'.format(p))
                list = self.scrapeList(category, p)
                self.saveList(list)


    def scrapeList(self, category, p):
        logging.info('Kickass scraping {0} page {1}'.format(category, p))
        res = requests.get('{0}/{1}/{2}'.format(self.URL_BASE, category, p), timeout=59)
        res.raise_for_status()
        soup = BeautifulSoup(res.content)
        table = soup.find('table', class_='data')
        list = []
        for tr in table.find_all('tr')[2:]:
            item = {}
            link = tr.find('a', class_='cellMainLink')
            item['url'] = link['href']
            item['title'] = link.text
            item['uploader'] = tr.find('div', class_='torrentname').find('a', class_='plain').text
            item['magnet'] = tr.find('a', class_='imagnet')['href']
            item['size'] = tr.find_all('td')[1].text
            item['files'] = tr.find_all('td')[2].text
            item['uploaded_at'] = tr.find_all('td')[3].text
            item['seeders'] = int(tr.find_all('td')[4].text)
            item['leechers'] = int(tr.find_all('td')[5].text)
            item['category'] = category
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



class Imdb():
    # urlBase = 'http://www.metacritic.com/search/%s/%s/results?sort=relevancy'
    urlSearch = r'http://www.imdb.com/find?q=%s&&s=tt&ref_=fn_tt_pop'

    def runMovies(self):
        categories = [201, 207]
        for code in categories:
            # print 'runmovies'
            category = Category.objects.get(code=code)
            # print category
            # print 'torrents'
            torrents = category.torrent_set.all()
            # print len(torrents)
            for torrent in torrents:
                if torrent.rated_at and arrow.get(torrent.rated_at) >= arrow.utcnow().replace(weeks=-2):
                    continue
                    # pass

                matches = re.match(r'(.*)\(?(194[5-9]|19[5-9]\d|200\d|201[0-9])', torrent.title)
                if matches is None:
                    logging.info('No match for ' + torrent.title)
                else:
                    title = matches.group(1).replace('(', '') + matches.group(2)
                    links = self.searchTitle(title)
                    rating, header = self.searchTitleRanking(links)
                    if not rating or not header:
                        continue

                    if r'1080p' in torrent.title.lower():
                        torrent.resolution = 1080
                    elif r'720p' in torrent.title.lower():
                        torrent.resolution = 720
                    torrent.title_rating = header
                    torrent.rating = rating
                    torrent.rated_at = arrow.utcnow().datetime
                    torrent.save()
                    logging.info('Saved ' + torrent.title)
                    time.sleep(0.1)
                    # break


    def searchTitle(self, title):
        links = []
        url = self.urlSearch % (title,)
        s = requests.Session()
        a = requests.adapters.HTTPAdapter(max_retries=3)
        s.mount('http://', a)
        headers = {
            # 'X-Real-IP': '251.223.201.178',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'
        }
        res = s.get(url, timeout=10, headers=headers)
        res.raise_for_status()
        # print res.content

        soup = BeautifulSoup(res.content)
        try:
            rows = soup.find('table', class_='findList').find_all('tr')
            for row in rows:
                links.append(row.find('a')['href'])
        except AttributeError:
            logging.error('No table or rows in response!')

        return links


    def searchTitleRanking(self, links):
        for link in links:
            url = r'http://www.imdb.com' + link
            s = requests.Session()
            a = requests.adapters.HTTPAdapter(max_retries=3)
            s.mount('http://', a)
            headers = {
                # 'X-Real-IP': '251.223.201.178',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'
            }
            res = s.get(url, timeout=10, headers=headers)
            res.raise_for_status()
            # print res.content

            soup = BeautifulSoup(res.content)
            try:
                rating = soup.find(class_=['star-box', 'giga-star']).find(class_=['titlePageSprite', 'star-box-giga-star']).text.strip()
                header = soup.find('h1', class_='header').find('span', class_='itemprop').text.strip()
                rating = int(float(rating)*10)
                return [rating, header]
            except AttributeError:
                logging.error('No star box rating for title!')

        return [None, None]



class SeriesScraper():
    def __init__(self):
        from google.appengine.api import urlfetch
        urlfetch.set_default_fetch_deadline(60)


    def run(self):
        for code in [205, 208]:
            category = Category.objects.get(code=code)
            seriesTitles = self.extractSeriesTitles(category)
            # self.scrapeSeriesTitles(seriesTitles, category)


    def extractSeriesTitles(self, category):
        titles = set()
        logging.debug('category', category)
        not_founds = []
        for torrent in category.torrent_set.filter(series_title__isnull=True, created_at__gte=arrow.now().replace(days=-7).datetime):
            # print 'torrent', torrent
            titleGroups = re.match(r'(.*)(s\d{1,2})(e\d{1,2})', torrent.title, re.I)
            if titleGroups is not None:
                titles.add(titleGroups.group(0))
                torrent.series_title = titleGroups.group(1).replace('.', ' ').strip()
                torrent.series_season = int(titleGroups.group(2)[1:])
                torrent.series_episode = int(titleGroups.group(3)[1:])
                torrent.save()
            else:
                not_founds.append(torrent.title)
        logging.debug('series titles', titles)

        # email not found titles
        mail.send_mail_to_admins(
            sender='jacoj82@gmail.com',
            subject="Series titles not found",
            body="\n".join(not_founds)
        )

        return titles


    def scrapeSeriesTitles(self, seriesTitles, category):
        s = requests.Session()
        a = requests.adapters.HTTPAdapter(max_retries=3)
        s.mount('http://', a)
        for seriesTitle in seriesTitles:
            res = s.get('http://www.thepiratebay.se/search/{0}/0/7/{1}'.format(seriesTitle, category.code), timeout=10)
            res.raise_for_status()
            scraper = Scraper()
            data = scraper.parseResultList(res.content)
            scraper.saveData(data, category)
            time.sleep(1)


    def saveData(self, data, category):
        for item in data:
            item['category'] = category
            torrent, created = Torrent.objects.get_or_create(tpb_id=item['tpb_id'], defaults=item)
            for property, value in item.iteritems():
                setattr(torrent, property, value)
            torrent.save()