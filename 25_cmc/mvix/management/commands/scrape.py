import json
from datetime import date
from time import sleep

import requests
from bs4 import BeautifulSoup
from django.core.management import BaseCommand

from mvix.models import Snapshot, Cryptocurrency, Quote

URL_HOST = 'https://coinmarketcap.com'
URL_CMC_SNAPSHOTS = f'{URL_HOST}/historical/'


class Command(BaseCommand):
    help = 'Scrape CMC for data'

    def _scrape_snapshots(self) -> None:
        res = requests.get(URL_CMC_SNAPSHOTS)
        html = BeautifulSoup(res.text, 'html.parser')
        links = html.find_all('a', class_='historical-link')
        hrefs = [l['href'] for l in links]
        self.stdout.write(f'Found {len(hrefs)} links...')

        created_cnt = 0
        for href in hrefs:
            date_str = href.split('/')[2]
            snap_date = date(int(date_str[:4]), int(date_str[4:6]), int(date_str[6:]))
            snapshot, created = Snapshot.objects.get_or_create(
                snapped_at=snap_date,
                href=href)
            created_cnt += int(created)
        self.stdout.write(f'Created {created_cnt} new snapshots')

    def _scrape_pages(self) -> None:
        snapshots = Snapshot.objects.filter(completed=False).all()
        for snapshot in snapshots:
            self._scrape_page(snapshot)
            snapshot.completed = True
            snapshot.save()
            sleep(5)

    def _scrape_page(self, snapshot: Snapshot) -> None:
        res = requests.get(f'{URL_HOST}{snapshot.href}')
        res.raise_for_status()
        html = BeautifulSoup(res.text, 'html.parser')
        script = html.find(id='__NEXT_DATA__').string
        data = json.loads(script)
        listing = data['props']['initialState']['cryptocurrency']['listingHistorical']['data']
        created_cnt = 0
        for item in listing:
            cryptocurrency, _ = Cryptocurrency.objects.get_or_create(
                symbol=item['symbol'],
                defaults={
                    'name': item['name'],
                    'slug': item['slug'],
                    'added_at': item['date_added']
                })
            quote, created = Quote.objects.get_or_create(
                snapshot=snapshot,
                cryptocurrency=cryptocurrency,
                rank=item['rank'],
                defaults={
                    'max_supply': item['max_supply'],
                    'circulating_supply': item['circulating_supply'],
                    'total_supply': item['total_supply'],
                    'price': item['quote']['USD']['price'],
                    'volume_24h': item['quote']['USD']['volume_24h'] or 0,
                    'change_7d': item['quote']['USD']['percent_change_7d'] or 0,
                    'market_cap': item['quote']['USD']['market_cap']
                })
            created_cnt += int(created)
        self.stdout.write(f'Created {created_cnt} new quotes on {snapshot.snapped_at}')

    def handle(self, *args, **options):
        self.stdout.write('Scraping coinmarketcap historical snapshots...')
        self._scrape_snapshots()
        self._scrape_pages()
