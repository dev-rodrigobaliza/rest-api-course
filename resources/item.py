from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required

from libs.i18n import get_text
from models.item import ItemModel
from schemas.item import ItemSchema

item_schema = ItemSchema()
items_schema = ItemSchema(many=True)


class Item(Resource):
    @classmethod
    @jwt_required()
    def get(cls, name: str):
        item = ItemModel.find_by_name(name)

        if item:
            return item_schema.dump(item), 200
        return {"message": get_text("item_not_found")}, 404

    @classmethod
    @jwt_required()
    def post(cls, name: str):
        if ItemModel.find_by_name(name):
            return {"message": get_text("item_name_exists").format(name)}, 400

        item_json = request.get_json()
        item_json["name"] = name

        item = item_schema.load(item_json)

        try:
            item.save_to_db()
        except:
            return {"message": get_text("item_insert_error")}, 500

        return item_schema.dump(item), 201

    @classmethod
    @jwt_required()
    def delete(cls, name: str):
        item = ItemModel.find_by_name(name)

        if item:
            item.delete_from_db()
            return {"message": get_text("item_deleted")}, 200
        return {"message": get_text("item_not_found")}, 404

    @classmethod
    @jwt_required()
    def put(cls, name: str):
        item_json = request.get_json()

        item = ItemModel.find_by_name(name)

        if item:
            item.price = item_json["price"]
        else:
            item_json["name"] = name
            item = item_schema.load(item_json)

        item.save_to_db()

        return item_schema.dump(item), 200


class ItemList(Resource):
    @classmethod
    @jwt_required()
    def get(cls):
        return {"items": items_schema.dump(ItemModel.find_all())}, 200
