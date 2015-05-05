import logging as log
from django import http
from django.shortcuts import render
from main import Main
from stats import Stats
from datetime import datetime


def home(request):
    log.info('Request: home')

    stats = Stats()

    return render(request, 'binary/home.html', {
        'q_values': stats.q.data,
        'runs_latest': stats.runs[-30:],
        'time_frames': stats.summarizeTimeFrames(),
        'trade_bases': stats.summarizeTradeBases(),
        'trade_aims': stats.summarizeTradeAims(),
    })


def run(request):
    log.info('Run started')

    # check if weekday is 1..5
    today = datetime.utcnow()
    if today.isoweekday() not in range(1, 6):
        log.info('Weekend: no trading')
    else:
        # start trading
        main = Main()
        main.saveQ()
        main.new()
        main.existing()
        main.saveQ()

    log.info('Run ended')
    return http.HttpResponse()


def notify(request):
    log.info('Request Notifying me')

    # check if weekday is 1..5
    today = datetime.utcnow()
    if today.isoweekday() not in range(1, 6):
        log.info('Weekend: no trading')
    else:
        main = Main(False)
        main.notifyMe()

    log.info('Request Me notified')
    return http.HttpResponse()
