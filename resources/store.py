from flask_restful import Resource

from libs.i18n import get_text
from models.store import StoreModel
from schemas.store import StoreSchema

store_schema = StoreSchema()
stores_schema = StoreSchema(many=True)


class Store(Resource):
    @classmethod
    def get(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            return store_schema.dump(store), 200
        return {"message": get_text("store_not_found")}, 404

    @classmethod
    def post(cls, name: str):
        if StoreModel.find_by_name(name):
            return {"message": get_text("store_name_exists").format(name)}, 400

        store = StoreModel(name=name)
        try:
            store.save_to_db()
        except:
            return {"message": get_text("store_insert_error")}, 500

        return store_schema.dump(store), 201

    @classmethod
    def delete(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()
            return {"message": get_text("store_deleted")}, 200

        return {"message": get_text("store_not_found")}, 404


class StoreList(Resource):
    @classmethod
    def get(cls):
        return {"stores": stores_schema.dump(StoreModel.find_all())}, 200
