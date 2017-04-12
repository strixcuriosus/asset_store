"""Shared utilities for testing purposes."""

import unittest
from run import app, db
from asset_store.models import Asset

# TODO: dynamically build a list of invalid asset dicts, too

VALID_ASSET_DICTS = []

# construct a list of some valid and invalid assets
name_base = 'f-11235_'
# consider all asset types
for asset_type_choice in Asset.ASSET_TYPES:
    asset_type = asset_type_choice[0]

    # follow rules about valid asset classes based on asset type
    if asset_type == Asset.SATELLITE:
        valid_classes = Asset.SATELLITE_CLASSES
    elif asset_type == Asset.ANTENNA:
        valid_classes = Asset.ANTENNA_CLASSES
    else:
        # add other asset type/class pairings here
        pass

    # consider all valid asset classes given the asset type
    for asset_class_choice in valid_classes:
        asset_class = asset_class_choice[0]
        # determine possible asset details based on asset class
        valid_details = [{}]
        if asset_class == Asset.DISH:
            valid_details.extend([{'diameter': 1.1}, {'radome': True}, {'diameter': 1.1, 'radome': False}])
        elif asset_class == Asset.YAGI:
            valid_details.append({'gain': 1.1})
        # consider a sampling of valid details based on asset class
        for i, details in enumerate(valid_details):
            name = name_base + asset_class[:2] + asset_type[:2] + str(i)
            VALID_ASSET_DICTS.append({'asset_class': asset_class,
                                      'asset_name': name,
                                      'asset_type': asset_type,
                                      'asset_details': details})


# a testing base class with a custom setUp
class AppTestCase(unittest.TestCase):
    """Custom base class to configure app with a test database."""

    def setUp(self):
        """Custom setup to use a temporary database."""
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        db.init_app(app)
        db.app = app
        with app.app_context():
            db.create_all()
        self.app = app.test_client()
