import logging
from google.appengine.api import mail
from src.main.models import Torrent, UserTorrent
import arrow


class Cleaner():

    def clean(self):
        logging.info('Cleaner: cleaning...')
        results = []

        # fetch old torrents
        cutoff = arrow.utcnow().replace(days=-28).datetime
        torrents = Torrent.query(Torrent.updated_at < cutoff).order(Torrent.updated_at).fetch()
        logging.info('{0} torrents found that is older than {1}'.format(len(torrents), cutoff))

        # delete old torrents
        for torrent in torrents:
            results.append(torrent.title)
            torrent.key.delete()
            logging.info('Deleted T {0}'.format(torrent.title.encode('utf-8')))

            # cleaning associated user torrents
            uts = UserTorrent.query(UserTorrent.torrent == torrent.key).fetch()
            logging.info('{0} usertorrents found that is invalid'.format(len(uts)))
            for ut in uts:
                results.append(str(ut.key.id()))
                ut.key.delete()
                logging.info('Deleted UT {0}'.format(ut.key.id()))

        mail.send_mail(
            sender='jacoj82@gmail.com',
            to='jacoj82@gmail.com',
            subject="Torrents cleaned",
            body='\n'.join(results),
        )

        logging.info('Cleaner: cleaned')