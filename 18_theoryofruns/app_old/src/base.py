import webapp2
from google.appengine.api import users
from src.main.piratebay import PirateBay


class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        webapp2.RequestHandler.dispatch(self)

    @webapp2.cached_property
    def template_values(self):
        pirate_bay = PirateBay()
        # Add the navigation categories to the values for every view
        # category_groups = CategoryGroup.query().order(CategoryGroup.code).fetch()
        # categories = Category.query().order(Category.code).fetch()
        return {
            'groups': pirate_bay.GROUPS,
        }

    @webapp2.cached_property
    def user(self):
        return users.get_current_user()
