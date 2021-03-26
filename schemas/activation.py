from libs.ma import ma
from models.activation import ActivationModel


class ActivationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ActivationModel
        dump_only = ("id", "expired_at", "confirmed")
        load_only = ("user",)
        include_fk = True
        load_instance = True
