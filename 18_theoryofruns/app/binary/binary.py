import json
import logging as log
import urllib, urllib2
from httplib import HTTPException
from cookielib import CookieJar
from bs4 import BeautifulSoup
from google.appengine.api import urlfetch
from pprint import pprint


class Binary():
    def __init__(self, auto_login):
        urlfetch.set_default_fetch_deadline(60)
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(CookieJar()))
        self.opener.addheaders = [
            ('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:36.0) Gecko/20100101 Firefox/36.0')]
        self.url_login = 'https://www.binary.com/login?l=EN'
        self.url_statement = 'https://www.binary.com/user/statement?l=EN'
        self.url_profit_table = 'https://www.binary.com/d/profit_table.cgi?l=EN'
        self.url_prices = 'https://www.binary.com/d/trade_price.cgi'
        self.url_purchase = 'https://vr-deal01.binary.com/c/trade.cgi'
        self.username = 'VRTC609286'
        self.password = 'binary2com'
        if auto_login:
            self.login()


    def login(self):
        log.info('Binary logging in...')
        formdata = {
            'loginid': self.username,
            'password': self.password,
        }
        data_encoded = urllib.urlencode(formdata)
        for _ in range(5):
            try:
                response = self.opener.open(self.url_login, data_encoded)
                log.info('Binary auth response {0}'.format(response.getcode()))
                if '<span class="clientid">VRTC609286</span>' not in response.read():
                    raise Exception('Could not log into Binary.com')
                break
            except HTTPException as e:
                log.warn('Could not log in...')
        else:
            raise e
        log.info('Binary logged in')


    def getStatement(self):
        log.info('Binary: statement retrieving...')

        response = self.opener.open(self.url_statement)
        html = BeautifulSoup(response.read())
        table = html.find('div', id='statement-table')
        if not table:
            raise Exception('No html table in statement')

        statement = {}
        for row in table.find_all('div', class_='table-body'):
            divs = row.find_all('div', recursive=False)
            # log.info('{0} divs in row'.format(len(divs)))
            ref = divs[0].find_all('div')[-1].text
            # log.info('{0}'.format(ref))
            payout = divs[2].find('span').text
            # log.info('payout div {0}'.format(divs[2]))
            # log.info('Ref {0} payout {1}'.format(ref, payout))
            statement[ref] = payout

        log.info('Binary: statement retrieved {0}'.format(len(statement)))
        return statement


    def getProfitTable(self):
        log.info('Binary: profit table retrieving...')

        response = self.opener.open(self.url_profit_table)
        html = BeautifulSoup(response.read())
        table = html.find('div', id='profit-table')
        if not table:
            raise Exception('No html table found')

        profit_table = {}
        for row in table.find_all('div', class_='table-body'):
            divs = row.find_all('div', recursive=False)
            # log.info('{0} divs in row'.format(len(divs)))
            ref = divs[0].find_all('div')[1].text
            # log.info('{0}'.format(ref))
            profit_loss = float(divs[2].find_all('div')[-1].text.replace(',', '').strip())
            # log.info('payout div {0}'.format(divs[2]))
            # log.info('Ref {0} profit/loss {1}'.format(ref, profit_loss))
            profit_table[ref] = profit_loss

        log.info('Binary: profit table retrieved {0}'.format(len(profit_table)))
        return profit_table


    def createNew(self, run):
        log.info('Binary trade creating...')

        for _ in xrange(5):

            # get prices
            prices = self.getPrices(run)
            item = self.filterTradeFromPrices(run, prices)

            # update payout if martingale
            if run.step > 1:
                profit_required = abs(run.profit_parent) + (1 / float(run.step))

                # calculate correct payout with probabilities
                run.payout = round(profit_required / (1 - item['payload']['prob']), 2)
                log.info('Payout updated to {0:.2f} for required profit of {1:.2f}'.format(run.payout, profit_required))

                # get price with updated payout
                prices = self.getPrices(run)
                item = self.filterTradeFromPrices(run, prices)

            run.probability = item['payload']['prob']

            # create request
            req = urllib2.Request(item['url'], data=urllib.urlencode(item['payload']))

            # submit
            res = self.purchaseTrade(req)
            if not res['success']:
                log.info('Create purchase try {0} failed'.format(_))
                continue

            # finished
            run.binary_ref = res['ref']
            run.stake = res['stake']
            return True

        log.info('Binary trade creation failed')
        return False


    def getPrices(self, run):
        log.info('Binary prices retrieving...')
        payload = {
            'l': 'EN',
            'submarket': 'major_pairs',
            'date_start': 'now',
            'expiry_type': 'duration',
            'duration_units': 'm',
            'expiry_date': '',
            'expiry_time': '',
            'pip_size': '',
            'amount_type': 'payout',
            'currency': 'USD',
            'barrier_type': 'relative',
            'market': 'forex',
            'showohlc': 'yes',
            'controller_action': 'price_box',
            'form_name': 'risefall',
            'form_parent': 'risefall',
            'extratab': 'intradayprices',
            't': '%PREFIX%',
            'ajax_only': 1,
            'price_only': 1,
        }
        payload['underlying_symbol'] = 'frx{0}'.format('EURUSD')
        payload['st'] = 'frx{0}'.format('EURUSD')
        payload['duration_amount'] = run.time_frame
        payload['expiry'] = '{0}m'.format(run.time_frame)
        payload['amount'] = run.payout
        log.info('Params: {0}'.format(payload))

        data_encoded = urllib.urlencode(payload)
        res = self.opener.open(self.url_prices, data_encoded)
        # log.info(res.read())

        html = BeautifulSoup(res.read())
        html_forms = html.find_all('form', class_='orderform')
        # log.info('html forms {0}'.format(html_forms))
        data = []
        for form in html_forms:
            item = {
                'url': form['action'],
                'payload': {
                    'ajax_only': 1,
                },
            }
            for input in form.find_all('input'):
                val = input['value'] if input['name'] not in ['payout', 'price', 'prob', 'opposite_prob'] else float(input['value'])
                item['payload'][input['name']] = val
            log.info('Binary prices form {0}'.format(item))
            data.append(item)

        log.info('Binary {0} prices retrieved'.format(len(data)))
        return data


    def purchaseTrade(self, req):
        log.info('Binary trade purchasing...')

        res = self.opener.open(req).read()
        # pprint(res)

        # decode
        res = json.loads(res)
        # pprint(res)

        # error?
        if 'error' in res:
            log.warn(res['error'])
            return {'success': False, 'error': res['error']}

        ref = res['trade_ref']
        html = BeautifulSoup(res['display'])
        stake = float(html.find('span', id='contract-outcome-buyprice').text)

        log.info('Binary trade purchased {0} with stake {1:.2f}'.format(ref, stake))
        return {'success': True, 'ref': ref, 'stake': stake}


    def filterTradeFromPrices(self, run, prices):
        log.info('Binary filtering prices...')

        payouts = [prices[0]['payload']['payout'], prices[1]['payload']['payout']]

        # selection is based on trade (base and aim)
        if run.trade_base == 'payout':
            # aim: highest = > payout
            if run.trade_aim == 'higher':
                if payouts[0] > payouts[1]:
                    item = prices[0]
                    log.info('{0} & {1} = {2:.2f} on rise'.format(run.trade_base, run.trade_aim, payouts[0]))
                else:
                    item = prices[1]
                    log.info('{0} & {1} = {2:.2f} on fall'.format(run.trade_base, run.trade_aim, payouts[1]))
            else:
                if payouts[0] > payouts[1]:
                    item = prices[1]
                    log.info('{0} & {1} = {2:.2f} on rise'.format(run.trade_base, run.trade_aim, payouts[1]))
                else:
                    item = prices[0]
                    log.info('{0} & {1} = {2:.2f} on fall'.format(run.trade_base, run.trade_aim, payouts[0]))

        elif run.trade_base == 'directional':
            # aim: highest => rise
            if run.trade_aim == 'higher':
                item = prices[0]
                log.info('{0} & {1} = {2:.2f} on rise'.format(run.trade_base, run.trade_aim, payouts[0]))
            else:
                item = prices[1]
                log.info('{0} & {1} = {2:.2f} on fall'.format(run.trade_base, run.trade_aim, payouts[1]))

        else:
            raise Exception('Unknown trade base {0}'.format(run.trade_base))

        log.info('Binary filtered prices')
        return item
