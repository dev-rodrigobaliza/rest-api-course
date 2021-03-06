from libs.ma import ma
from models.store import StoreModel
from schemas.item import ItemSchema


class StoreSchema(ma.SQLAlchemyAutoSchema):
    items = ma.Nested(ItemSchema, many=True)

    class Meta:
        model = StoreModel
        dump_only = ("id", "activated")
        include_fk = True
        load_instance = True
