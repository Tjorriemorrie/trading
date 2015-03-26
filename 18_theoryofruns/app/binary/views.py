import logging as log
from django import http
from main import Main
from datetime import datetime


def home(request):
    log.info('Home requested')
    return http.HttpResponse('Go fuck yourself')


def run(request):
    log.info('Run started')

    # check if weekday is 1..5
    today = datetime.now()
    if today.isoweekday() not in range(1, 6):
        log.info('Weekend: no trading')
    else:
        # start trading
        main = Main()
        main.new()
        main.existing()
        main.saveQ()

    log.info('Run ended')
    return http.HttpResponse()


def notify(request):
    log.info('Request Notifying me')

    # check if weekday is 1..5
    today = datetime.now()
    if today.isoweekday() not in range(1, 6):
        log.info('Weekend: no trading')
    else:
        main = Main(False)
        main.notifyMe()

    log.info('Request Me notified')
    return http.HttpResponse()
