import logging as log
from django import http
from main import Main


def home(request):
    log.info('Home requested')
    return http.HttpResponse('Go fuck yourself')


def run(request):
    log.info('Run started')
    main = Main()

    # create new
    main.new()

    # finish existing
    main.existing()

    # save model
    main.saveQ()

    # end
    log.info('Run ended')
    return http.HttpResponse()
