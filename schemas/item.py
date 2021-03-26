from libs.ma import ma
from models.item import ItemModel
from models.store import StoreModel


class ItemSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ItemModel
        dump_only = ("id",)
        load_only = ("store",)
        include_fk = True
        load_instance = True
