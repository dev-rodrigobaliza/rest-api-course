import os
from dotenv import load_dotenv

from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_uploads import configure_uploads, patch_request_class
from marshmallow import ValidationError

from libs.ma import ma
from libs.db import db
from libs.bc import bc
from libs.im import IMAGE_SET
from libs.i18n import change_locale
from blacklist import BLACKLIST
from resources.user import UserRegister, UserLogin, User, TokenRefresh, UserLogout
from resources.item import Item, ItemList
from resources.store import Store, StoreList
from resources.activation import Activation, ActivationByUser
from resources.image import ImageUpload, Image, AvatarUpload, Avatar


MAX_UPLOAD_SIZE = 10 * 1024 * 1024

change_locale("en-us")
# change_locale("pt-br")

app = Flask(__name__)
load_dotenv(".env", verbose=True)
app.config.from_object("default_config")
app.config.from_envvar("APP_SETTINGS")

patch_request_class(app, MAX_UPLOAD_SIZE)
configure_uploads(app, IMAGE_SET)

api = Api(app, prefix="/api/v1")


@app.before_first_request
def create_tables():
    db.init_app(app)
    db.create_all()


@app.errorhandler(ValidationError)
def handle_marshmallow_validation(err):
    return jsonify(err.messages), 400


@app.after_request
def add_header(response):
    # just for the fun ;)
    response.headers['server'] = "obnoxious"
    response.headers['X-Powered-By'] = "creativity"
    return response


jwt = JWTManager(app)


@jwt.additional_claims_loader
# Remember identity is what we define when creating the access token
def add_claims_to_jwt(identity):
    if (identity == 1):  # instead of hard-coding, we should read from a file or database to get a list of admins instead
        return {"is_admin": True}
    return {"is_admin": False}


# This method will check if a token is blacklisted, and will be called automatically when blacklist is enabled
@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_headers, jwt_payload):
    # Here we blacklist particular JWTs that have been created in the past.
    return (jwt_payload["jti"] in BLACKLIST)


# The following callbacks are used for customizing jwt response/error messages.
# The original ones may not be in a very pretty format (opinionated)
@jwt.expired_token_loader
def expired_token_callback(jwt_headers, jwt_payload):
    return jsonify({"message": "The token has expired.", "error": "token_expired"}), 401


@jwt.invalid_token_loader
# we have to keep the argument here, since it's passed in by the caller internally
def invalid_token_callback(error):
    return (jsonify({"message": "Signature verification failed.", "error": "invalid_token"}), 401)


@jwt.unauthorized_loader
def missing_token_callback(error):
    return (jsonify({"description": "Request does not contain an access token.", "error": "authorization_required"}), 401)


@jwt.needs_fresh_token_loader
def token_not_fresh_callback(jwt_headers, jwt_payload):
    return (jsonify({"description": "The token is not fresh.", "error": "fresh_token_required"}), 401)


@jwt.revoked_token_loader
def revoked_token_callback(jwt_headers, jwt_payload):
    return (jsonify({"description": "The token has been revoked.", "error": "token_revoked"}), 401)


api.add_resource(Store, "/store/<string:name>")
api.add_resource(StoreList, "/stores")
api.add_resource(Item, "/item/<string:name>")
api.add_resource(ItemList, "/items")
api.add_resource(UserRegister, "/register")
api.add_resource(Activation, "/user_activate/<string:activation_id>")
api.add_resource(ActivationByUser, "/activation/user/<int:user_id>")
api.add_resource(User, "/user/<int:user_id>")
api.add_resource(UserLogin, "/login")
api.add_resource(TokenRefresh, "/refresh")
api.add_resource(UserLogout, "/logout")
api.add_resource(ImageUpload, "/upload/image")
api.add_resource(Image, "/image/<string:filename>")
api.add_resource(AvatarUpload, "/upload/avatar")
api.add_resource(Avatar, "/avatar/<int:user_id>")

if __name__ == "__main__":
    db.init_app(app)
    ma.init_app(app)
    bc.init_app(app)

    app.run()
