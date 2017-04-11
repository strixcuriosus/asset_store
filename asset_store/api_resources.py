"""RESTful Asset Store API Resources (RASAR)."""
import six

from flask_restplus import abort, Api, fields, reqparse, Resource
from sqlalchemy.orm.exc import NoResultFound

from asset_store.models import Asset, db
from asset_store.utils import ResourceConflictError, ValidationError

# the api is implemented with flask-restplus, which comes with some swaggerific tools for easy auto-documentations
api = Api(version='0.1', title='Asset Store API.',
          description='A RESTful web API for satellite and antenna assets.')

# a parser for asset create args
asset_parser = reqparse.RequestParser()
asset_parser.add_argument('asset_name', required=True)
asset_parser.add_argument('asset_type', required=True)
asset_parser.add_argument('asset_class', required=True)


# asset fields to expose in the api
ASSET_FIELDS_TO_SERIALIZE = {'asset_name': fields.String(default='HelloWorld'),
                             'asset_type': fields.String(attribute=lambda x: x.asset_type.value, default='satellite'),
                             'asset_class': fields.String(attribute=lambda x: x.asset_class.value, default='dove')}


# an api model can be used to marshal (aka serialize) the data model into json
ASSET_RESOURCE_FIELDS = api.model('Asset', ASSET_FIELDS_TO_SERIALIZE)


@api.route('/assets/<asset_name>')
@api.doc(params={'asset_name': 'unique name of the asset'})
class AssetResource(Resource):
    """A single asset resource."""

    @api.response(200, 'Success')
    @api.response(400, 'ValidationError')
    @api.response(404, 'Asset Not Found')
    @api.marshal_with(ASSET_RESOURCE_FIELDS)
    def get(self, asset_name=None):
        """Get a single Asset."""
        if not isinstance(asset_name, six.string_types):
            abort(400, message='asset_name must be a string.')
        try:
            asset = db.session.query(Asset).filter(Asset.asset_name == asset_name).one()
            return asset, 200
        except NoResultFound:
            abort(404, message='asset with name {} not found.'.format(asset_name))


@api.route('/assets')
@api.response(400, 'ValidationError')
class AssetListResource(Resource):
    """A collection resource of asset resources."""

    @api.response(200, 'Success')
    @api.marshal_with(ASSET_RESOURCE_FIELDS, as_list=True)
    def get(self):
        """Get a list of assets."""
        assets = db.session.query(Asset).all()
        return assets, 200

    @api.response(201, 'Asset Created')
    @api.expect(ASSET_RESOURCE_FIELDS)
    def post(self):
        """Create a new asset."""
        asset_dict = asset_parser.parse_args()
        try:
            Asset.create_asset(**asset_dict)
            return asset_dict, 201
        except ValidationError as err:
            abort(400, message='{}'.format(err))
        except ResourceConflictError as err:
            abort(409, message='{}'.format(err))
