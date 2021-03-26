import traceback
from time import time

from flask import make_response, render_template
from flask_restful import Resource

from libs.i18n import get_text
from libs.mg import MailgunException
from models.activation import ActivationModel
from models.user import UserModel
from schemas.activation import ActivationSchema

activation_schema = ActivationSchema()


class Activation(Resource):
    @classmethod
    def get(cls, activation_id: str):
        activation = ActivationModel.find_by_id(activation_id)
        if not activation:
            return {"message": get_text("activation_not_found")}, 404

        if activation.expired:
            return {"message": get_text("activation_expired")}, 400

        if activation.activated:
            return {"message": get_text("activation_activated")}, 400

        activation.activated = True
        activation.save_to_db()

        headers = {"Content-Type": "text/html"}
        return make_response(render_template("activation_page.html", email=activation.user.email), 200, headers)


class ActivationByUser(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": get_text("user_not_found")}, 404

        return (
            {
                "current_time": int(time()),
                "activation": [
                    activation_schema.dump(each)
                    for each in user.activation.order_by(ActivationModel.expire_at)
                ]
            },
            200
        )

    @classmethod
    def post(cls, user_id: int):
        """Resend activation email"""
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": get_text("user_not_found")}, 404

        try:
            activation = user.most_recent_activation
            if activation:
                if activation.activated:
                    return {"message": get_text("activation_activated")}, 400

                activation.force_to_expire()

            new_activation = ActivationModel(user_id)
            new_activation.save_to_db()
            user.send_confirmation_email()
            return {"message": get_text("activation_resend_successful")}, 201
        except MailgunException as err:
            return {"message": err.message}, 500
        except:
            traceback.print_exc()
            return {"message": get_text("activation_resend_error")}, 500
