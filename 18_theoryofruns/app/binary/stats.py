import logging as log
from google.appengine.ext import ndb
from models import Run, Q
from pprint import pprint
from models import CURRENCIES, TRADE_BASES, TRADE_AIMS


class Stats():

    def __init__(self):
        log.info('Stat init started')
        self.loadQ()
        self.runs = Run.query().order(Run.ended_at).fetch()
        log.info('Main init ended')


    def loadQ(self):
        log.info('Q loading...')
        q_key = ndb.Key(Q, 'main')
        self.q = q_key.get()
        if not self.q:
            self.q = Q(key=q_key, data={})
        log.info('Q loaded {0}'.format(len(self.q.data)))


    def summarizeTimeFrames(self):
        log.info('Stats summarizing time frames...')
        time_frames = {tf: 0 for tf in TIME_FRAMES}
        for run in self.runs:
            if run.stake and run.profit:
                time_frames[run.time_frame] += run.profit / run.stake
                time_frames[run.time_frame] /= 2
        log.info('Stats summarized time frames...')
        return time_frames


    def summarizeTradeBases(self):
        log.info('Stats summarizing trade bases...')
        trade_bases = {tb: 0 for tb in TRADE_BASES}
        for run in self.runs:
            if run.stake and run.profit:
                trade_bases[run.trade_base] += run.profit / run.stake
                trade_bases[run.trade_base] /= 2
        log.info('Stats summarized trade bases...')
        return trade_bases


    def summarizeTradeAims(self):
        log.info('Stats summarizing trade aims...')
        trade_aims = {tb: 0 for tb in TRADE_AIMS}
        for run in self.runs:
            if run.stake and run.profit:
                trade_aims[run.trade_aim] += run.profit / run.stake
                trade_aims[run.trade_aim] /= 2
        log.info('Stats summarized trade aims...')
        return trade_aims
