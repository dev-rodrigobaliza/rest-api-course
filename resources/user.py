import traceback
from flask import request, make_response, render_template
from flask_restful import Resource
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt

from libs.bc import bc
from libs.mg import MailgunException
from schemas.user import UserSchema
from models.user import UserModel
from blacklist import BLACKLIST

USER_EXISTS = "A user with that username already exists."
EMAIL_EXISTS = "A user with that email already exists."
ERROR_REGISTERING = "An error occurred while registering the user."
REGISTERED_SUCCESSFULLY = "User created successfully, an email with an activation link has been sent to the email address, awaiting confirmation to activate de account."
USER_NOT_FOUND = "User not found."
USER_DELETED = "User deleted."
INVALID_CREDENTIALS = "Invalid credentials!"
USER_LOGGED_OUT = "User <id={}> successfully logged out."
NOT_CONFIRMED_ERROR = "You have not confirmed registration, please check your email <{}>."
USER_ACTIVATED = "User <id={}> has been already activated previously!"
ERROR_ACTIVATING = "An error occurred while activating the user."
ACTIVATED_SUCCESSFULLY = "User activated successfully."

user_schema = UserSchema()


class UserRegister(Resource):
    @classmethod
    def post(cls):
        user = user_schema.load(request.get_json())

        if UserModel.find_by_username(user.username):
            return {"message": USER_EXISTS}, 400

        if UserModel.find_by_email(user.email):
            return {"message": EMAIL_EXISTS}, 400

        user.password = bc.generate_password_hash(user.password)

        try:
            user.save_to_db()
            user.send_confirmation_email()
            return {"message": REGISTERED_SUCCESSFULLY}, 201
        except MailgunException as err:
            user.delete_from_db()
            return {"message": err.message}, 500
        except:
            traceback.print.exc()
            return {"message": ERROR_REGISTERING}, 500


class User(Resource):
    @classmethod
    @jwt_required()
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404
        return user_schema.dump(user), 200

    @classmethod
    @jwt_required()
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404
        user.delete_from_db()
        return {"message": USER_DELETED}, 200


class UserLogin(Resource):
    @classmethod
    def post(cls):
        user_data = user_schema.load(request.get_json(), partial=("email",))

        user = UserModel.find_by_username(user_data.username)

        if user and user.verify_password(user_data.password):
            if user.activated:
                access_token = create_access_token(
                    identity=user.id, fresh=True)
                refresh_token = create_refresh_token(user.id)
                return {"access_token": access_token, "refresh_token": refresh_token}, 200
            return {"message": NOT_CONFIRMED_ERROR.format(user.email)}, 40

        return {"message": INVALID_CREDENTIALS}, 401


class UserLogout(Resource):
    @classmethod
    @jwt_required()
    def post(cls):
        # jti is "JWT ID", a unique identifier for a JWT.
        jti = get_jwt()["jti"]
        user_id = get_jwt_identity()
        BLACKLIST.add(jti)
        return {"message": USER_LOGGED_OUT.format(user_id)}, 200


class TokenRefresh(Resource):
    @classmethod
    @jwt_required(refresh=True)
    def post(cls):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200


class UserActivate(Resource):
    @classmethod
    # @jwt_required()
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)

        if not user:
            return {"message": USER_NOT_FOUND}, 404

        if user.activated:
            return {"message": USER_ACTIVATED.format(user_id)}, 200

        user.activated = True

        try:
            user.save_to_db()
        except:
            return {"message": ERROR_ACTIVATING}, 500

        headers = {"Content-Type": "text/html"}
        return make_response(render_template("confirmation_page.html", email=user.email), 200, headers)
