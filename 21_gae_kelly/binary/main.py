import logging as log
import datetime as dt
import time
from google.appengine.ext import ndb
from google.appengine.api import mail
from models import Run, Q
from rl import RL
from binary import Binary
from pprint import pprint


class Main():

    def __init__(self, auto_login=True):
        log.info('Main init started')
        self.binary = Binary(auto_login)
        self.rl = RL()
        self.loadQ()
        log.info('Main init ended')


    def loadQ(self):
        log.info('Q loading...')

        q_key = ndb.Key(Q, 'main')
        self.q = q_key.get()
        if not self.q:
            self.q = Q(key=q_key)

        # validate properties
        if not self.q.data:
            self.q.data = {}
        if not self.q.visits:
            self.q.visits = {}
            runs = Run.query().fetch()
            for run in runs:
                if run.getState() not in self.q.visits:
                    self.q.visits[run.getState()] = 0
                self.q.visits[run.getState()] += 1

        log.info('Q loaded {0}'.format(len(self.q.data)))


    def saveQ(self):
        log.info('Q saving...')
        self.q.put()
        log.info('Q saved {0}'.format(len(self.q.data)))


    def new(self):
        '''Create new iteration'''
        log.info('Main new started')

        currency, time_frame, trade_base, trade_aim = self.rl.selectNew(self.q)
        run_key = ndb.Key('Run', str(dt.datetime.utcnow()))
        run = Run(
            key=run_key,
            currency=currency,
            time_frame=time_frame,
            trade_base=trade_base,
            trade_aim=trade_aim,
            step=1,
            payout=1.,
            ended_at=dt.datetime.utcnow() + dt.timedelta(minutes=int(time_frame)),
        )

        if self.binary.createNew(run):
            run.put()
            log.info('New run: {0}'.format(run))

        log.info('Main new ended')


    def existing(self):
        '''Go through all existing iterations'''
        log.info('Main existing started')

        runs = Run.query(Run.is_finished == False).fetch()
        log.info('{0} runs found'.format(len(runs)))

        if len(runs):
            profit_table = self.binary.getProfitTable()

            # continue every run
            for run in runs:
                log.info('Run: finding profit for {0}'.format(run.binary_ref))

                # time frame ending?
                if run.ended_at > dt.datetime.utcnow() + dt.timedelta(seconds=60):
                    log.info('Run: skipping till {0}'.format(run.ended_at))
                    continue

                # wait for result
                profit_table_update_delay = dt.timedelta(seconds=15)
                to_sleep = max(0, int((run.ended_at - dt.datetime.utcnow() + profit_table_update_delay).total_seconds()))
                if to_sleep > 0:
                    log.info('Run: waiting for {0} seconds'.format(to_sleep))
                    time.sleep(to_sleep + 5)
                    log.info('Run: refreshing profit table...')
                    profit_table = self.binary.getProfitTable()

                # get result
                if run.binary_ref in profit_table:
                    parent_stake = run.stake_parent if run.stake_parent else 0.
                    run.profit = profit_table[run.binary_ref]
                    run.profit_net = run.profit + run.profit_parent
                    run.stake_net = run.stake + parent_stake
                    run.is_win = True if run.profit > 0 else False
                    run.is_finished = True
                    run.put()
                    log.info('Run: finished with profit {0:.2f}'.format(run.profit))

                    # continue to cancel loss?
                    if not run.is_win:
                        run_child = self.martingale(run)
                    else:
                        # update q
                        self.q = self.rl.updateQ(self.q, run)
                else:
                    log.error('{0} has no profit/loss in table'.format(run.binary_ref))

        log.info('Main existing ended')


    def martingale(self, run_parent):
        log.info('Martingale: loss for {0}'.format(run_parent.binary_ref))

        # a child is born
        run_child_key = ndb.Key('Run', str(dt.datetime.utcnow()))
        run_child = Run(
            key=run_child_key,
            currency=run_parent.currency,
            time_frame=run_parent.time_frame,
            trade_base=run_parent.trade_base,
            trade_aim=run_parent.trade_aim,

            parent_run=run_parent.key,
            profit_parent=run_parent.profit_net,
            stake_parent=run_parent.stake,

            step=run_parent.step + 1,
            payout=run_parent.payout * 2,
            ended_at=dt.datetime.utcnow() + dt.timedelta(minutes=int(run_parent.time_frame)),
        )

        # a child is registered
        if self.binary.createNew(run_child):
            run_child.put()
            log.info('New martingale run: {0}'.format(run_child))

        log.info('Martingale: created new run')
        return run_child


    def notifyMe(self):
        log.info('Main Notifying me')

        log.info('Main waiting for trading to finish')
        time.sleep(60)
        log.info('Main waiting finished')

        started_at = dt.datetime.utcnow() + dt.timedelta(hours=-1)
        ended_at = dt.datetime.utcnow()
        runs = Run.query(Run.ended_at >= started_at, Run.ended_at <= ended_at, Run.is_finished == True, Run.is_win == True).fetch()
        log.info('Fetched {0} runs from {1} till {2}'.format(len(runs), started_at, ended_at))

        # exit if nothing
        if not runs:
            log.warn('Exiting as there is no runs!')
            return

        net_profit = 0.
        stakes = 0.
        runs_size = len(runs) + 0.

        fields = ['binary_ref', 'time_frame', 'trade_base', 'trade_aim', 'step', 'profit_parent', 'stake_parent', 'stake', 'probability', 'payout', 'profit_net']
        # table header
        table = '<table width=100%" border="1"><thead><tr>'
        for field in fields:
            table += '<th>{0}</th>'.format(field)
        table += '</tr></thead>'
        # table body
        table += '<tbody>'
        for run in runs:
            # update results
            net_profit += run.profit_net
            stakes += run.stake

            row = '<tr>'
            for field in fields:
                row += '<td>{0}</td>'.format(getattr(run, field))
            row += '</tr>'
            log.info('Row: {0}'.format(row))
            table += row

            while run.step > 1:
                run = run.parent_run.get()
                stakes += run.stake

                row = '<tr><td>&nbsp;</td>'
                for field in fields[1:-1]:
                    row += '<td>{0}</td>'.format(getattr(run, field))
                row += '<td>&nbsp;</td></tr>'
                log.info('Row: {0}'.format(row))
                table += row

        table += '</tbody></table>'
        # pprint(table)

        subject = '[{0:.2f}] {1} runs totalling {2:.2f} profit with {3:.2f} stakes'.format(
            net_profit / stakes,
            runs_size,
            net_profit,
            stakes,
        )
        log.info('Subject: {0}'.format(subject))

        msg = mail.EmailMessage(
            sender='jacoj82@gmail.com',
            subject=subject,
            to='jacoj82@gmail.com',
        )

        msg.body = table

        msg.html = '<html><body>' + table + '</body></html>'

        msg.send()

        log.info('Main Me notified')
