"""Database backed models for the asset store."""

import re
import six

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String
from sqlalchemy.exc import IntegrityError
from sqlalchemy_utils import ChoiceType

from asset_store.utils import get_choice_list, ResourceConflictError, ValidationError, validate_choice

db = SQLAlchemy()


class Asset(db.Model):
    """A model for tracking satellite and antenna assets."""

    # types
    ANTENNA = 'antenna'
    SATELLITE = 'satellite'

    ASSET_TYPES = [(SATELLITE, 'satellite'),
                   (ANTENNA, 'antenna')]

    # type specific classes
    ANTENNA_CLASSES = [('dish', 'dish'),
                       ('yagi', 'yagi')]

    SATELLITE_CLASSES = [('dove', 'dove'),
                         ('rapideye', 'rapideye')]

    # all classes
    ASSET_CLASSES = ANTENNA_CLASSES + SATELLITE_CLASSES

    # model fields
    id = Column(Integer, primary_key=True)
    asset_name = Column(String(64), nullable=False, unique=True)
    asset_type = Column(ChoiceType(ASSET_TYPES), nullable=False)
    asset_class = Column(ChoiceType(ASSET_CLASSES), nullable=False)

    @classmethod
    def create_asset(cls, asset_name, asset_type, asset_class):
        """Create a new instance of an Asset.

        Args:
            asset_name (string): name of the new asset. Must meet the following constraints:
                                    1. must start with an alphanumeric character
                                    2. can only contain alphanumeric characters, dashses, and underscores
                                    3. can be no longer than 64 characters
                                    4. can be no shorter than 4 characters
                                    5. can not already be used as an existing asset's asset_name
            asset_type (string): the type of asset. Valid types are 'satellite' and 'antenna'
            asset_class (string): the class of the asset. Valid classes depend on the asset_type.
                                      - Valid classes for 'satellite' asset_type are 'dove' and 'rapideye'
                                      - Valid classes for 'antenna' asset_type are 'dish' and 'yagi'
        Returns:
            asset: a newly created Asset instance
        Raises:
            ValidationError: the provided arguments do not meet validation constraints
            IntegrityError
        """
        from run import app
        cls._validate_asset_name(asset_name)
        cls._validate_asset_type(asset_type)
        cls._validate_asset_class(asset_class)
        cls._validate_asset_class_with_asset_type(asset_class, asset_type)

        with app.app_context():
            try:
                asset = Asset(asset_name=asset_name, asset_type=asset_type, asset_class=asset_class)
                db.session.add(asset)
                db.session.commit()
            except IntegrityError as err:
                if 'UNIQUE constraint failed: asset.asset_name' in '{}'.format(err):
                    raise ResourceConflictError('There is already an asset with asset_name {}'.format(asset_name))
        return asset

    # The following methods are for validating asset fields.
    # To better enforce some of the business rules, additional database constraints could be added in the future.

    @classmethod
    def _validate_asset_type(cls, asset_type):
        """Check if an asset_type value is valid.

        Args:
            asset_type (str): value representing an asset_type to be validated
        Returns:
            valid (bool): True if validation passed
        Raises:
            ValidationError: if provided asset_type value is not a valid choice
        """
        return validate_choice('asset_type', asset_type, cls.ASSET_TYPES)

    @classmethod
    def _validate_asset_class(cls, asset_class):
        """Check if an asset_type value is valid.

        Args:
            asset_class (str): value representing an asset_class to be validated
        Returns:
            valid (bool): True if validation passed
        Raises:
            ValidationError: if provided asset_class value is not a valid choice
        """
        return validate_choice('asset_class', asset_class, cls.ASSET_CLASSES)

    @classmethod
    def _validate_asset_class_with_asset_type(cls, asset_class, asset_type):
        """Check if an asset_class value is valid for a given asset_type.

        Args:
            asset_type (str): value representing an asset_type to be validated
            asset_class (str): value representing an asset_class to be validated
        Returns:
            valid (bool): True if validation passed
        Raises:
            ValidationError: if provided asset_class value is not a valid choice given the provided asset_type
        """
        error_msg = 'Invalid asset_class. For the {} asset_type, valid asset_class values are: {}'
        if asset_type == cls.ANTENNA:
            choices = get_choice_list(cls.ANTENNA_CLASSES)
            error_msg = error_msg.format(cls.ANTENNA, choices)
            return validate_choice('asset_class', asset_class, cls.ANTENNA_CLASSES,
                                   custom_error_msg=error_msg)
        elif asset_type == cls.SATELLITE:
            choices = get_choice_list(cls.SATELLITE_CLASSES)
            error_msg = error_msg.format(cls.SATELLITE, choices)
            return validate_choice('asset_class', asset_class, cls.SATELLITE_CLASSES,
                                   custom_error_msg=error_msg)
        else:
            raise ValidationError('Unrecognized asset_type {}'.format(asset_type))

    @classmethod
    def _validate_asset_name(cls, asset_name):
        """Check if an asset_name value is valid.

        Args:
            asset_name (str): value representing an asset_name to be validated
        Returns:
            valid (bool): True if validation passed
        Raises:
            ValidationError: if provided asset_name has one of the following issues:
                - is shorter than 4 characters
                - is longer than 64 characters
                - has already used by another asset
                - starts with a '-' or '_'
        """
        if not isinstance(asset_name, six.string_types):
            raise ValidationError('asset_name must be a string.')

        length = len(asset_name)
        if length < 4:
            raise ValidationError('asset_name must be at least 4 characters in length.')
        if length > 64:
            raise ValidationError('asset_name must be at most 64 characters in length.')

        first_char = asset_name[0]
        if first_char in ['-', '_']:
            raise ValidationError('asset_name cannot begin with an underscore or dash.')

        # should start with an alphanum and all subsequent characters should be alphanum or dashes
        if re.match('^[0-9a-zA-Z]+[0-9a-zA-Z_-]*$', asset_name) is None:
            raise ValidationError('asset_name may only contain alphanumeric ascii characters, underscores, and dashes.')

        return True
