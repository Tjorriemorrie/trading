import logging as log
from django import http
from django.shortcuts import render
from main import Main
from stats import Stats
from datetime import datetime
from google.appengine.ext import ndb
import time
from google.appengine.api import mail


def home(request):
    log.info('Request: home')
    return http.HttpResponse()


def run(request):
    log.info('Run started')

    try:
        main = Main()
        main.new()
        main.existing()
        main.saveQ()
    except Exception as e:
        log.error(e)
        notifyError(e)

    log.info('Run ended')
    return http.HttpResponse()


def notify(request):
    log.info('Request Notifying me')

    # check if weekday is 1..5
    # today = datetime.utcnow()
    # if today.isoweekday() not in range(1, 6):
    #     log.info('Weekend: no trading')
    # else:
    main = Main(False)
    main.notifyMe()

    log.info('Request Me notified')
    return http.HttpResponse()


def delete(request):
    log.info('Request delete!')
    from models import Run
    runs_keys = Run.query().fetch(keys_only=True)
    ndb.delete_multi(runs_keys)
    log.info('Deleted runs')
    return http.HttpResponse()


def close(request):
    log.info('Request close!')
    from models import Run
    runs = Run.query(Run.is_finished == False).fetch()
    log.info('{0} unfinished'.format(len(runs)))
    for run in runs:
        run.is_finished = True
        run.put()
        log.info('Run closed {0}'.format(run.binary_ref))
    return http.HttpResponse()


def notifyError(e):
    log.info('Error notifying...')
    msg = mail.EmailMessage(
        sender='jacoj82@gmail.com',
        subject='Error',
        to='jacoj82@gmail.com',
        body='{0}'.format(e),
    )
    msg.send()
    log.info('Error notified')