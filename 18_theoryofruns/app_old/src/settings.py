import os
import jinja2
from webapp2 import uri_for


DEBUG = False

SECRET_KEY = 'asdfjasdflkjsfewi23kjl3kjl45kjl56jk6hjb76vsjsa'

CONFIG = {
}


SRC_ROOT = os.path.dirname(os.path.realpath(__file__))

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(SRC_ROOT),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True,
)
JINJA_ENVIRONMENT.globals['uri_for'] = uri_for
