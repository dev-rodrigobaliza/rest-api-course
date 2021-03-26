from libs.ma import ma
from models.user import UserModel


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserModel
        dump_only = ("id",)
        load_only = ("password",)
        load_instance = True
