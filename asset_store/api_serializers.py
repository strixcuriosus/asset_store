"""RequestParsers and api models for serialization."""

from flask_restplus import fields, reqparse
from asset_store.utils import PartialDictField

# a parser for assets
asset_parser = reqparse.RequestParser()
asset_parser.add_argument('asset_name', required=True)
asset_parser.add_argument('asset_type', required=True)
asset_parser.add_argument('asset_class', required=True)
asset_parser.add_argument('asset_details', type=dict)

# a parser for asset_details
asset_details_parser = reqparse.RequestParser()
asset_details_parser.add_argument('gain')
asset_details_parser.add_argument('diameter')
asset_details_parser.add_argument('radome')

# a parser for asset list filter args
asset_filters_parser = reqparse.RequestParser()
asset_filters_parser.add_argument('asset_type', location='args')
asset_filters_parser.add_argument('asset_class', location='args')


# asset fields to expose in the api
ASSET_FIELDS_TO_SERIALIZE = {'asset_name': fields.String(default='HelloWorld'),
                             'asset_type': fields.String(attribute=lambda x: x.asset_type.value, default='antenna'),
                             'asset_class': fields.String(attribute=lambda x: x.asset_class.value, default='dish'),
                             'asset_details': PartialDictField}

ASSET_DETAILS_FIELDS_TO_SERIALIZE = {'gain': fields.Float(),
                                     'diameter': fields.Float(),
                                     'radome': fields.Boolean()}
