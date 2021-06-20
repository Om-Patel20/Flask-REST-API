import os

from flask import Flask
from flask_restful import Api
from flask_jwt import JWT

from security import authenticate, identity # Separate python file
from resources.user import UserRegister
from resources.item import Item
from resources.item import ItemList
from resources.store import Store
from resources.store import StoreList

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'ohm'
api = Api(app)

jwt = JWT(app, authenticate, identity) # /auth (i.e. new endpoint)

# Now we tell our API that the resource we have created (i.e. Student)
# is now going to be accessible through our API.
api.add_resource(Store, '/store/<string:name>')
api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(StoreList, '/stores')
api.add_resource(UserRegister, '/register')

if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run(port = 5000, debug=True)

# Status code for 'Not Found' is 404
# Status code for creating is 201