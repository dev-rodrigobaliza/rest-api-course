import traceback

from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt

from libs.i18n import get_text
from libs.bc import bc
from libs.mg import MailgunException
from schemas.user import UserSchema
from models.user import UserModel
from models.activation import ActivationModel
from blacklist import BLACKLIST

user_schema = UserSchema()


class UserRegister(Resource):
    @classmethod
    def post(cls):
        user = user_schema.load(request.get_json())

        if UserModel.find_by_username(user.username):
            return {"message": get_text("user_name_exists")}, 400

        if UserModel.find_by_email(user.email):
            return {"message": get_text("user_email_exists")}, 400

        user.password = bc.generate_password_hash(user.password)

        try:
            user.save_to_db()

            activation = ActivationModel(user.id)
            activation.save_to_db()

            user.send_confirmation_email()
            return {"message": get_text("user_register_successful")}, 201
        except MailgunException as err:
            user.delete_from_db()
            return {"message": err.message}, 500
        except:
            traceback.print_exc()
            user.delete_from_db()
            return {"message": get_text("user_register_error")}, 500


class User(Resource):
    @classmethod
    @jwt_required()
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": get_text("user_not_found")}, 404
        return user_schema.dump(user), 200

    @classmethod
    @jwt_required()
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": get_text("user_not_found")}, 404
        user.delete_from_db()
        return {"message": get_text("user_deleted")}, 200


class UserLogin(Resource):
    @classmethod
    def post(cls):
        user_data = user_schema.load(request.get_json(), partial=("email",))

        user = UserModel.find_by_username(user_data.username)

        if user and user.verify_password(user_data.password):
            activation = user.most_recent_activation
            if activation and activation.activated:
                access_token = create_access_token(
                    identity=user.id, fresh=True)
                refresh_token = create_refresh_token(user.id)
                return {"access_token": access_token, "refresh_token": refresh_token}, 200

            return {"message": get_text("user_not_activated").format(user.email)}, 40

        return {"message": get_text("user_invalid_credentials")}, 401


class UserLogout(Resource):
    @classmethod
    @jwt_required()
    def post(cls):
        # jti is "JWT ID", a unique identifier for a JWT.
        jti = get_jwt()["jti"]
        user_id = get_jwt_identity()
        BLACKLIST.add(jti)
        return {"message": get_text("user_logged_out").format(user_id)}, 200


class TokenRefresh(Resource):
    @classmethod
    @jwt_required(refresh=True)
    def post(cls):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200
