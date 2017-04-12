"""API Tests."""
import ddt
import json

from collections import defaultdict

from asset_store.models import Asset
from .test_utils import AppTestCase, VALID_ASSET_DICTS


@ddt.ddt
class AssetsAPITestCase(AppTestCase):
    """AssetResource and AssetListResource tests."""

    def test_get_assets_list__empty(self):
        """The assets endpoint should return an empty list if there are no assets."""
        response = self.app.get('/assets')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.get_data()), [])

    @ddt.data(*VALID_ASSET_DICTS)
    def test_get_assets_list__one(self, asset_dict):
        """The assets endpoint should return a list of all assets."""
        Asset.create_asset(**asset_dict)
        expected_result = [asset_dict]
        response = self.app.get('/assets')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.get_data()), expected_result)

    def test_get_assets_list__multiple(self):
        """The assets endpoint should return a list of all assets."""
        Asset.create_asset(**VALID_ASSET_DICTS[0])
        Asset.create_asset(**VALID_ASSET_DICTS[1])
        response = self.app.get('/assets')
        self.assertEqual(response.status_code, 200)
        results = json.loads(response.get_data())
        self.assertEqual(results, VALID_ASSET_DICTS[:2])

    def test_get_assets_list__filtered(self):
        """Test asset_type and asset_class filtering."""
        # create many valid assets
        for asset_dict in VALID_ASSET_DICTS:
            Asset.create_asset(**asset_dict)

        # no supported filters
        response = self.app.get('/assets?foo=bar')
        results = json.loads(response.get_data())
        self.assertEqual(len(results), len(VALID_ASSET_DICTS))

        # filter by type
        response = self.app.get('/assets?asset_type=satellite')
        results = json.loads(response.get_data())
        self.assertGreater(len(results), 0)
        self.assertTrue(all([res['asset_type'] == Asset.SATELLITE for res in results]))

        # filter by class
        response = self.app.get('/assets?asset_class=yagi')
        results = json.loads(response.get_data())
        self.assertGreater(len(results), 0)
        self.assertTrue(all([res['asset_class'] == Asset.YAGI for res in results]))

        # filter by type and class
        response = self.app.get('/assets?asset_type=antenna&asset_class=yagi')
        results = json.loads(response.get_data())
        self.assertGreater(len(results), 0)
        self.assertTrue(all([res['asset_class'] == Asset.YAGI and
                             res['asset_type'] == Asset.ANTENNA for res in results]))

        # filter by invalid type
        response = self.app.get('/assets?asset_type=atypical')
        results = json.loads(response.get_data())
        self.assertEqual(len(results), 0)

        # filter by invalid (type, class) pair
        response = self.app.get('/assets?asset_type=satellite&asset_class=yagi')
        results = json.loads(response.get_data())
        self.assertEqual(len(results), 0)

    @ddt.data(*VALID_ASSET_DICTS)
    def test_get_single_asset_by_name__valid(self, asset_dict):
        """The single asset endpoint should return a single asset if it exists."""
        Asset.create_asset(**asset_dict)
        name = asset_dict['asset_name']
        path = '/assets/{}'.format(name)
        response = self.app.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.get_data()), asset_dict)

    @ddt.data('foo', 'bogus_non-existent', 'ok' * 33, 1, 2.0, -3, {'hello': 'earth'}, None)
    def test_get_single_asset_by_name__404(self, name):
        """The assets endpoint should return a 404 for a non-existent asset_name."""
        path = '/assets/{}'.format(name)
        response = self.app.get(path)
        self.assertEqual(response.status_code, 404)
        message = json.loads(response.get_data()).get('message', '')
        self.assertIn('not found', message)

    @ddt.data(*VALID_ASSET_DICTS)
    def test_get_asset_details_by_asset_name(self, asset_dict):
        """The asset_details endpoint should return asset_details for an asset."""
        Asset.create_asset(**asset_dict)
        name = asset_dict['asset_name']
        path = '/assets/{}/details'.format(name)
        response = self.app.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.get_data()), asset_dict['asset_details'])

    @ddt.data(*VALID_ASSET_DICTS)
    def test_update_asset_details_by_asset_name(self, asset_dict):
        """The asset_details endpoint should return asset_details for an asset."""
        classes_to_details = defaultdict(lambda: {}, {Asset.DISH: {'diameter': '1.2321', 'radome': 'true'},
                                                      Asset.YAGI: {'gain': '2.79'}})

        Asset.create_asset(**asset_dict)
        name = asset_dict['asset_name']
        path = '/assets/{}/details'.format(name)

        new_details = classes_to_details[asset_dict['asset_class']]
        response = self.app.put(path, data=new_details)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(json.loads(response.get_data()), new_details)

    # TODO: handle mal-formed non-dict data edge cases (e.g. 'hello', 1.23)
    @ddt.data({'diameter': 'hello', 'radome': '1.23', 'cat': 'meow'}, {'gain': 'hello'})
    def test_update_asset_details_by_asset_name__invalid_details(self, invalid_details):
        """The asset_details endpoint should not allow invalid update of asset_details."""
        asset_dict = VALID_ASSET_DICTS[0]
        Asset.create_asset(**asset_dict)
        name = asset_dict['asset_name']
        path = '/assets/{}/details'.format(name)
        response = self.app.put(path, data=invalid_details)
        self.assertEqual(response.status_code, 400)

    # Note: It would be more user-friendly to support an optional backslash for the asset list resource
    def test_get_single_asset_by_name__404__no_name(self):
        """The assets endpoint should return a 404 for an empty string asset_name."""
        path = '/assets/'
        response = self.app.get(path)
        self.assertEqual(response.status_code, 404)

    @ddt.data(*VALID_ASSET_DICTS)
    def test_create_asset__success(self, asset_dict):
        """The assets endpoint should support asset creation."""
        response = self.app.post('/assets', data=json.dumps(asset_dict), content_type='application/json',
                                 headers={'X-User': 'admin'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(json.loads(response.get_data()), asset_dict)

    @ddt.data({'X-User': 'badminton'}, {}, None)
    def test_create_asset__not_authorized(self, non_admin_headers):
        """The assets endpoint should support asset creation."""
        asset_dict = VALID_ASSET_DICTS[0]
        response = self.app.post('/assets', data=json.dumps(asset_dict), content_type='application/json',
                                 headers=non_admin_headers)
        self.assertEqual(response.status_code, 403)

    @ddt.data(*VALID_ASSET_DICTS)
    def test_create_asset__duplicate__no_details(self, asset_dict):
        """The assets endpoint should not allow creation of 2 assets with the same name."""
        # TODO: fix test client post with details
        asset_dict = asset_dict.copy()
        del asset_dict['asset_details']
        # create 1st asset
        self.app.post('/assets', data=asset_dict, headers={'X-User': 'admin'})
        # try creating another asset with the same asset data
        response = self.app.post('/assets', data=asset_dict, headers={'X-User': 'admin'})
        self.assertEqual(response.status_code, 409)
        message = json.loads(response.get_data()).get('message', '')
        expected_message = 'There is already an asset with asset_name {}'.format(asset_dict['asset_name'])
        self.assertEqual(message, expected_message)

    @ddt.data(*VALID_ASSET_DICTS)
    def test_asset_delete_not_allowed(self, asset_dict):
        """The assets endpoint does not support asset deletion."""
        Asset.create_asset(**asset_dict)
        path = '/assets/{}'.format(asset_dict['asset_name'])
        response = self.app.delete(path)
        # 405 method not allowed
        self.assertEqual(response.status_code, 405)

    @ddt.data(*VALID_ASSET_DICTS)
    def test_asset_update_not_allowed(self, asset_dict):
        """The assets endpoint does not support asset update."""
        Asset.create_asset(**asset_dict)
        path = '/assets/{}'.format(asset_dict['asset_name'])
        response = self.app.put(path, data={'asset_class': 'rapideye'})
        self.assertEqual(response.status_code, 405)
