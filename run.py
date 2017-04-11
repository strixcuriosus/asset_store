"""This Asset Store is implemented as a Flask app with a RESTful web API."""
from flask import Flask

from asset_store.api_resources import api, AssetResource, AssetListResource
from asset_store.models import db

# yay, it's a flask app!
# since the purpose of this project is to implement a demo RESTful web api in python,
# the lightweight tools and flexibility of the flask microframwork seemed apt
app = Flask(__name__)

# if this project were to grow, these configurations could config file
# if these needed to be more flexible or secret, environment variables could be used to populate the configs
app.config['SWAGGER_UI_DOC_EXPANSION'] = 'list'

# for simplicity, just use sqlite for now.
# note: since this project is using sqlalchemy to abstract database interfaces,
#       sqlite could easily be replaecd with a more robust relational db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/asset_store.db'

# this setting is necessary to avoid pending deprecation warnings from sqlalchemy
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# initialize flask app models and api resources
api.init_app(app)
db.init_app(app)

# create the database tables when the app runs
with app.app_context():
    db.create_all()

api.add_resource(AssetListResource, '/assets')
api.add_resource(AssetResource, '/assets/<asset_name>')

if __name__ == '__main__':
    # host is set for supporting docker port binding
    # debug is on for testing purposes
    app.run(host='0.0.0.0', debug=True)
