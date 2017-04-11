"""Model Tests."""
import ddt

from asset_store.models import Asset
from asset_store.utils import ValidationError
from .test_utils import AppTestCase


NON_STRINGS = [11235, 2.2, {'some': 'dict'}, ['listy', 'list']]


@ddt.ddt
class AssetsModelTestCase(AppTestCase):
    """Tests for the Asset model."""

    @ddt.data('satellite', 'antenna')
    def test_validate_asset_type__valid(self, asset_type):
        """Should pass for valid asset_type values."""
        self.assertTrue(Asset._validate_asset_type(asset_type))

    @ddt.data('satellllllite', 'hello', 'debris', 'wormhole', 'sat', 'ant', 'dove')
    def test_validate_asset_type__invalid_value(self, asset_type):
        """Should raise ValidationError for invalid asset_type values."""
        with self.assertRaisesRegexp(ValidationError, 'is not a valid choice for asset_type'):
            Asset._validate_asset_type(asset_type)

    @ddt.data(*NON_STRINGS)
    def test_validate_asset_type__invalid_type(self, asset_type):
        """Should raise ValidationError for invalid asset_type values."""
        with self.assertRaisesRegexp(ValidationError, 'asset_type must be a string.'):
            Asset._validate_asset_type(asset_type)

    @ddt.data('dove', 'rapideye', 'dish', 'yagi')
    def test_validate_asset_class__valid(self, asset_class):
        """Should pass for valid asset_class values."""
        self.assertTrue(Asset._validate_asset_class(asset_class))

    @ddt.data('pigeon', 'sloweye', 'dash', 'yagi-uda', 'antenna', 'satellite')
    def test_validate_asset_class__invalid_value(self, asset_class):
        """Should raise ValidationError for invalid asset_class values."""
        with self.assertRaisesRegexp(ValidationError, 'is not a valid choice for asset_class'):
            Asset._validate_asset_class(asset_class)

    @ddt.data(*NON_STRINGS)
    def test_validate_asset_class__invalid_class(self, asset_class):
        """Should raise ValidationError for invalid asset_class values."""
        with self.assertRaisesRegexp(ValidationError, 'asset_class must be a string.'):
            Asset._validate_asset_class(asset_class)

    @ddt.data(('satellite', 'dove'),
              ('satellite', 'rapideye'),
              ('antenna', 'dish'),
              ('antenna', 'yagi'))
    @ddt.unpack
    def test_validate_asset_class_with_asset_type__valid_pairs(self, asset_type, asset_class):
        """Should pass for valid (asset_type, asset_class) pairs."""
        self.assertTrue(Asset._validate_asset_class_with_asset_type(asset_class, asset_type))

    @ddt.data(('satellite', 'dish'),
              ('satellite', 'yagi'),
              ('satellite', 'foo'),
              ('foo', 'dish'),
              ('foo', 'dove'),
              ('antenna', 'dove'),
              ('antenna', 'rapideye'),
              ('antenna', 'foo'))
    @ddt.unpack
    def test_validate_asset_class_with_asset_type__ivalid_pairs(self, asset_type, asset_class):
        """Should raise ValidationError for invalid (asset_type, asset_class) pairs."""
        with self.assertRaises(ValidationError):
            self.assertTrue(Asset._validate_asset_class_with_asset_type(asset_class, asset_type))

    @ddt.data('a' * 4, 'a' * 64, 'hello', 'asset_name')
    def test_validate_asset_name__valid(self, asset_name):
        """Should pass for valid asset_name values."""
        self.assertTrue(Asset._validate_asset_name(asset_name))

    @ddt.data('a' * 3, 'a' * 65, '-hello', '_asset_name')
    def test_validate_asset_name__invalid(self, asset_name):
        """Should pass for valid asset_name values."""
        with self.assertRaises(ValidationError):
            Asset._validate_asset_name(asset_name)
