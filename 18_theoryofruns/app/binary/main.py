import logging as log
import datetime as dt
import time
from google.appengine.ext import ndb
from google.appengine.api import mail
from models import Run, Q
from rl import RL
from binary import Binary


class Main():

    def __init__(self):
        log.info('Main init started')
        self.epsilon = 0.05
        self.binary = Binary()
        self.rl = RL()
        self.loadQ()
        log.info('Main init ended')


    def loadQ(self):
        log.info('Q loading...')
        q_key = ndb.Key(Q, 'main')
        self.q = q_key.get()
        if not self.q:
            self.q = Q(key=q_key, data={})
        log.info('Q loaded {0}'.format(len(self.q.data)))


    def saveQ(self):
        log.info('Q saving...')
        self.q.put()
        log.info('Q saved {0}'.format(len(self.q.data)))


    def new(self):
        '''Create new iteration'''
        log.info('Main new started')

        currency, time_frame, trade_base, trade_aim = self.rl.selectNew(self.q.data, self.epsilon)
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
                if run.ended_at > dt.datetime.utcnow() + dt.timedelta(seconds=30):
                    log.info('Run: skipping till {0}'.format(run.ended_at))
                    continue

                # wait for result
                to_sleep = max(0, int((run.ended_at - dt.datetime.utcnow()).total_seconds()))
                if to_sleep > 0:
                    log.info('Run: waiting for {0} seconds'.format(to_sleep))
                    time.sleep(to_sleep + 5)
                    log.info('Run: refreshing profit table...')
                    profit_table = self.binary.getProfitTable()

                # get result
                if run.binary_ref in profit_table:
                    run.profit = profit_table[run.binary_ref]
                    run.profit_net = run.profit + run.profit_parent
                    run.is_win = True if run.profit > 0 else False
                    run.is_finished = True
                    run.put()
                    log.info('Run: finished with profit {0:.2f}'.format(run.profit))

                    # continue to cancel loss?
                    if not run.is_win:
                        run_child = self.martingale(run)
                    else:
                        self.notifyMe(run)
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


    def notifyMe(self, run):
        log.info('Notifying me')

        subject = '{0} with {1:.2f} after {2} steps\n\n'.format(run.binary_ref, run.profit_net, run.step)
        body = 'Currency: {0}\nTime frame: {1}\nTrade base: {2}\nTrade aim: {3}\n\n'.format(run.currency, run.time_frame, run.trade_base, run.trade_aim)
        fields = ['step', 'stake', 'payout', 'profit', 'profit_parent', 'profit_net']

        for field in fields:
            body += '{0}: {1}\n'.format(field, getattr(run, field))
        body += '\n\n'

        while run.step > 1:
            run = run.parent_run.get()
            for field in fields:
                body += '{0}: {1}\n'.format(field, getattr(run, field))
            body += '\n\n'

        mail.send_mail(
            sender='jacoj82@gmail.com',
            to='jacoj82@gmail.com',
            subject=subject,
            body=body,
        )
        log.info('Me notified')
