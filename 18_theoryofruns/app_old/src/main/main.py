import logging
from src.settings import JINJA_ENVIRONMENT
from src.base import BaseHandler
from src.main.models import Torrent, UserTorrent
from google.appengine.ext import ndb
from google.appengine.api import users
import arrow
from time import sleep


class IndexPage(BaseHandler):
    def get(self):
        # new movies
        self.template_values['movies'] = Torrent.query(Torrent.category_code == 207, Torrent.uploader == 'YIFY', Torrent.resolution == 720).order(-Torrent.uploaded_at).fetch(30)

        # new series
        self.template_values['series_new'] = Torrent.query(Torrent.category_code == 205, Torrent.series_episode == 1).order(-Torrent.uploaded_at).fetch(15)

        episodes_new = []
        series_watching = []

        # watching series
        uts = UserTorrent.query(UserTorrent.user == users.get_current_user(), UserTorrent.category_code == 205).fetch()
        if uts:
            series_watching = set()
            for ut in [ut for ut in uts if ut.torrent.get().series_title]:
                series_watching.add(ut.torrent.get().series_title)
            logging.info('{0} series being watched by user'.format(len(uts)))

            # new episodes
            if series_watching:
                cutoff = arrow.utcnow().replace(days=-14).datetime
                episodes_new = Torrent.query(Torrent.series_title.IN(series_watching), Torrent.uploaded_at > cutoff, Torrent.category_code == 205).order(-Torrent.uploaded_at).fetch()
                logging.info('{0} episodes fetched for watched series'.format(len(episodes_new)))

        self.template_values['series_watching'] = series_watching
        self.template_values['episodes_new'] = episodes_new

        # logging.info('{0}'.format(self.template_values))
        template = JINJA_ENVIRONMENT.get_template('main/templates/index.html')
        self.response.write(template.render(self.template_values))


class CategoryPage(BaseHandler):
    def get(self, cat):
        logging.info('cat {0}'.format(cat))
        self.template_values['cat'] = int(cat)

        # get torrents
        torrents = Torrent.query(Torrent.category_code == int(cat)).order(-Torrent.uploaded_at).fetch()
        self.template_values['torrents'] = torrents
        logging.info('torrents {0}'.format(len(torrents)))

        template = JINJA_ENVIRONMENT.get_template('main/templates/category.html')
        self.response.write(template.render(self.template_values))


class DownloadPage(BaseHandler):
    def get(self, key):
        logging.info('download {0}'.format(key))
        logging.info('user {0}'.format(self.user))
        torrent = ndb.Key(urlsafe=key).get()
        logging.info('torrent {0}'.format(torrent))
        ut = UserTorrent.query(UserTorrent.user == self.user, UserTorrent.torrent == torrent.key).get()
        if not ut:
            ut = UserTorrent(user=self.user, torrent=torrent.key, category_code=torrent.category_code)
            ut.put()
            logging.info('User Torrent saved')
        else:
            ut.key.delete()
            logging.info('User Torrent deleted')
        logging.info('User Torrent {0}'.format(ut))
        self.response.status = '200 OK'