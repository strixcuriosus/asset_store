"""Miscellaneous utilities for the asset_store app."""
import six
from flask_restplus import fields


# custom exeptions
class ValidationError(Exception):
    """Custom exception class for model validations."""

    pass


class ResourceConflictError(Exception):
    """Custom exception database conflicts."""

    pass


# choice field utils
def get_choice_list(list_of_choice_tuples):
    """Map a list of choice_tuples to a list of choice strings.

    Args:
        list_of_choice_tuples (list of tuples): ChoiceType list of tuples.

    Returns:
        list_of_choices (list of strings): list of raw choice string values.
    """
    return map(lambda x: x[0], list_of_choice_tuples)


def validate_choice(choice_name, choice_value, valid_choice_tuples, custom_error_msg=None):
    """Validate a choice string given a list of valid choice tuples.

    Args:
        choice_name (string): name of the field in for which a choice is being validated (e.g. 'asset_type')
        choice_value (string): value of the candidate choice
        valid_choice_tuples (list of tuples): ChoiceType list of tuples.
        custom_error_msg (string): custom error message to use if a ValidationError is raised

    Returns:
        valid (bool): True if the choice_value is valid give then list of valid_choice_tuples
    Raises:
        ValidationError: if choice_value is not valid
    """
    if not isinstance(choice_value, six.string_types):
        raise ValidationError('{} must be a string.'.format(choice_name))

    choice_list = get_choice_list(valid_choice_tuples)
    if choice_value in choice_list:
        return True
    else:
        if custom_error_msg:
            msg = custom_error_msg
        else:
            msg = '{} is not a valid choice for {}. Valid choices are: {}'.format(
                choice_value, choice_name, choice_list)
        raise ValidationError(msg)


def remove_nulls(input_dict):
    """Remove keys with no value from a dictionary."""
    output = {}
    for k, v in input_dict.items():
        if v is not None:
            output[k] = v
    return output


def has_admin_access(user):
    """Check if a user has admin access."""
    return user == 'admin'


# custom partial flask-restful field
class PartialDictField(fields.Raw):
    """A dict field that hides null values."""

    def format(self, value):
        """Convert dict value to masked dict."""
        return remove_nulls(value)
