import webapp2
from google.appengine.ext import ndb


class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        webapp2.RequestHandler.dispatch(self)

    @webapp2.cached_property
    def parent_key(self):
        return ndb.Key('artist', 'jeanne')
