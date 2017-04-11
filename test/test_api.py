"""API Tests."""
import ddt
import json

from asset_store.models import Asset
from .test_utils import AppTestCase, ASSET_DICT_0, ASSET_DICT_1


@ddt.ddt
class AssetsAPITestCase(AppTestCase):
    """AssetResource and AssetListResource tests."""

    def test_get_assets_list__empty(self):
        """The assets endpoint should return an empty list if there are no assets."""
        response = self.app.get('/assets')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.get_data()), [])

    def test_get_assets_list__one(self):
        """The assets endpoint should return a list of all assets."""
        Asset.create_asset(**ASSET_DICT_0)
        expected_result = [ASSET_DICT_0]
        response = self.app.get('/assets')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.get_data()), expected_result)

    def test_get_assets_list__multiple(self):
        """The assets endpoint should return a list of all assets."""
        Asset.create_asset(**ASSET_DICT_0)
        Asset.create_asset(**ASSET_DICT_1)
        expected_result = [ASSET_DICT_0, ASSET_DICT_1]
        response = self.app.get('/assets')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.get_data()), expected_result)

    def test_get_single_asset_by_name__valid(self):
        """The assets detail endpoint should return a single asset if it exists."""
        Asset.create_asset(**ASSET_DICT_0)
        name = ASSET_DICT_0['asset_name']
        path = '/assets/{}'.format(name)
        response = self.app.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.get_data()), ASSET_DICT_0)

    @ddt.data('foo', 'bogus_non-existent', 'ok' * 33, 1, 2.0, -3, {'hello': 'earth'}, None)
    def test_get_single_asset_by_name__404(self, name):
        """The assets endpoint should return a 404 for a non-existent asset_name."""
        path = '/assets/{}'.format(name)
        response = self.app.get(path)
        print(response)
        self.assertEqual(response.status_code, 404)
        message = json.loads(response.get_data()).get('message', '')
        self.assertIn('not found', message)

    # Note: It would be more user-friendly to support an optional backslash for the asset list resource
    def test_get_single_asset_by_name__404__no_name(self):
        """The assets endpoint should return a 404 for an empty string asset_name."""
        path = '/assets/'
        response = self.app.get(path)
        self.assertEqual(response.status_code, 404)

    def test_create_asset__success(self):
        """The assets enpoint should support asset creation."""
        response = self.app.post('/assets', data=ASSET_DICT_0)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(json.loads(response.get_data()), ASSET_DICT_0)

    def test_create_asset__duplicate(self):
        """The assets enpoint should not allow creation of 2 assets with the same name."""
        # create 1st asset
        self.app.post('/assets', data=ASSET_DICT_0)
        # try creating another asset with the same asset data
        response = self.app.post('/assets', data=ASSET_DICT_0)
        self.assertEqual(response.status_code, 409)
        message = json.loads(response.get_data()).get('message', '')
        self.assertEqual(message, 'There is already an asset with asset_name hello')

    def test_asset_delete_not_allowed(self):
        """The assets endpoint does not support asset deletion."""
        Asset.create_asset(**ASSET_DICT_0)
        path = '/assets/{}'.format(ASSET_DICT_0['asset_name'])
        response = self.app.delete(path)
        # 405 method not allowed
        self.assertEqual(response.status_code, 405)

    def test_asset_update_not_allowed(self):
        """The assets endpoint does not support asset update."""
        Asset.create_asset(**ASSET_DICT_0)
        path = '/assets/{}'.format(ASSET_DICT_0['asset_name'])
        response = self.app.put(path, data={'asset_class': 'rapideye'})
        self.assertEqual(response.status_code, 405)
