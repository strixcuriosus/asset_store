"""Shared utilities for testing purposes."""

import unittest
from run import app, db

# some dict representations of assets
ASSET_DICT_0 = {u'asset_class': u'dove', u'asset_name': u'hello', u'asset_type': u'satellite'}
ASSET_DICT_1 = {u'asset_class': u'yagi', u'asset_name': u'world', u'asset_type': u'antenna'}


# a testing base class with a custom setUp
class AppTestCase(unittest.TestCase):

    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        db.init_app(app)
        db.app = app
        with app.app_context():
            db.create_all()
        self.app = app.test_client()
