from flask_jwt_extended.utils import get_jwt_identity
from flask_restful import Resource
from flask_restful import reqparse # Important
from flask import request # Always remember
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    jwt_optional,
    get_jwt_claims,
    fresh_jwt_required
)
from models.item import ItemModel

# we do not need to do jsonify() with flask_restful because it does it for us.
class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price',
        type = float,
        required = True,
        help = 'This field cannot be left blank!'
    )
    parser.add_argument('store_id',
        type = int,
        required = True,
        help = 'Every item needs a store id.'
    )
    @jwt_required # You can put this on any method to require JSON web token & autherization header to execute
    def get(self, name):
        try:
            item = ItemModel.find_by_name(name)
        except:
            return {'message': 'Error occurred while executing this function.'}, 500

        if item:
            return item.json()
        return {'message': 'Item not found.'}, 404
    
    # POST has to have the same set of parameters.
    @fresh_jwt_required
    def post(self, name):
        if ItemModel.find_by_name(name):
            return {'message': f'An item with name {name} already exists'}, 400
        data = Item.parser.parse_args()
        item = ItemModel(name, **data) #or data['price'], data['store_id']

        try:
            item.save_to_db()
        except:
            return {'message': 'An error has occurred inserting the item.'}, 500 # Internal server error

        return item.json(), 201
    
    @jwt_required
    def delete(self, name):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'Admin privilege required.'}, 401
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
        
        return {'message': 'Item deleted'}
    
    def put(self, name):
        data = Item.parser.parse_args()

        item = ItemModel.find_by_name(name)
        if item is None:
            item = ItemModel(name, **data) # or data['price'], data['store_id']
        else:
            item.price = data['price']
            item.store_id = data['store_id']
        
        item.save_to_db()
        return item.json()


class ItemList(Resource):
    @jwt_optional
    def get(self):
        user_id = get_jwt_identity()
        items = [x.json() for x in ItemModel.find_all()]
        if user_id:
            return {'items': items}, 200
        return {'items': [item['name'] for item in items],
                'message': 'More data available if you log in.'
            }, 200
        # SELECT * FROM items
        # or return {'items': list(map(lambda x: x.json(), ItemModel.query.all()))}