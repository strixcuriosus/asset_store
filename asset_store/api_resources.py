"""RESTful Asset Store API Resources (RASAR)."""
import six

from flask import request
from flask_restplus import abort, Api, Resource
from sqlalchemy.orm.exc import NoResultFound

from asset_store.api_serializers import (asset_parser,
                                         asset_details_parser,
                                         asset_filters_parser,
                                         ASSET_FIELDS_TO_SERIALIZE,
                                         ASSET_DETAILS_FIELDS_TO_SERIALIZE)

from asset_store.models import Asset, db
from asset_store.utils import has_admin_access, remove_nulls, ResourceConflictError, ValidationError

# the api is implemented with flask-restplus, which comes with some swaggerific tools for easy auto-documentations
api = Api(version='0.2.2', title='Asset Store API.',
          description='A RESTful web API for satellite and antenna assets.')


# an api model can be used to marshal (aka serialize) the data model into json
ASSET_RESOURCE_FIELDS = api.model('Asset', ASSET_FIELDS_TO_SERIALIZE)
ASSET_DETAILS_RESOURCE_FIELDS = api.model('AssetDetails', ASSET_DETAILS_FIELDS_TO_SERIALIZE)


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


@api.response(200, 'Success')
@api.route('/assets/<asset_name>/details')
class AssetDetailsResource(Resource):
    """Update details for a single Asset."""

    def _get_asset(self, asset_name):
        """Get an asset by name."""
        if not isinstance(asset_name, six.string_types):
            abort(400, message='asset_name must be a string.')
        try:
            asset = db.session.query(Asset).filter(Asset.asset_name == asset_name).one()
        except NoResultFound:
            abort(404, message='asset with name {} not found.'.format(asset_name))
        return asset

    def get(self, asset_name=None):
        """Update details for a single Asset."""
        asset = self._get_asset(asset_name)
        return asset.asset_details

    @api.expect(ASSET_DETAILS_RESOURCE_FIELDS)
    def put(self, asset_name):
        """Update details for a single Asset.

        Replaces all details with the new provided details.
        Does not merge new details with old details (i.e. not doing an upsert)
        """
        try:
            dict(request.data)
        except TypeError:
            abort(400, message='asset_details must be a dict')

        asset_details = remove_nulls(asset_details_parser.parse_args())
        asset = self._get_asset(asset_name)

        try:
            asset.update_details(asset_details)
        except ValidationError as err:
            abort(400, message='{}'.format(err))
        return asset.asset_details


@api.route('/assets')
class AssetListResource(Resource):
    """A collection resource of asset resources."""

    @api.response(200, 'Success')
    @api.marshal_with(ASSET_RESOURCE_FIELDS, as_list=True)
    def get(self):
        """Get a list of assets."""
        filters = remove_nulls(asset_filters_parser.parse_args())
        assets = db.session.query(Asset).filter_by(**filters).all()
        return assets, 200

    @api.header('X-User', 'just a username for now', required=True)
    @api.response(201, 'Asset Created')
    @api.response(400, 'ValidationError')
    @api.response(403, 'Not Authorized')
    @api.expect(ASSET_RESOURCE_FIELDS)
    def post(self):
        """Create a new asset."""
        # check if user is authorized
        # TODO: consider making a reusable auth decorator
        user = request.headers.get('X-User')
        if not has_admin_access(user):
            abort(403, 'Not authorized to create assets.')
        asset_dict = dict(asset_parser.parse_args())
        # fill in default (empty dict) details if not provided
        asset_dict['asset_details'] = asset_dict['asset_details'] or {}
        try:
            Asset.create_asset(**asset_dict)
            return asset_dict, 201
        except ValidationError as err:
            abort(400, message='{}'.format(err))
        except ResourceConflictError as err:
            abort(409, message='{}'.format(err))
