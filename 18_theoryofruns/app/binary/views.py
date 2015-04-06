import logging as log
from django import http
from django.shortcuts import render
from main import Main
from stats import Stats
from datetime import datetime
from google.appengine.ext import ndb
import time


def home(request):
    log.info('Request: home')
    return http.HttpResponse()


def run(request):
    log.info('Run started')

    # check if weekday is 1..5
    # today = datetime.utcnow()
    # if today.isoweekday() not in range(1, 6):
    #     log.info('Weekend: no trading')
    # else:
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
