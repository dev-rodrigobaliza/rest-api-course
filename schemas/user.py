from marshmallow import pre_dump

from libs.ma import ma
from models.user import UserModel


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserModel
        dump_only = ("id", "activation")
        load_only = ("password",)
        load_instance = True

    @pre_dump
    def most_recent_activation(self, user: UserModel, many, **kwargs):
        user.activation = [user.most_recent_activation]
        return user
