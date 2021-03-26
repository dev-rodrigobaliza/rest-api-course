from flask import request, url_for
from requests import Response

from libs.db import db
from libs.bc import bc
from libs.mg import Mailgun
from models.activation import ActivationModel


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)

    activation = db.relationship(
        "ActivationModel", lazy="dynamic", cascade="all, delete-orphan")

    @property
    def most_recent_activation(self) -> "ActivationModel":
        return self.activation.order_by(db.desc(ActivationModel.expire_at)).first()

    @classmethod
    def find_by_username(cls, username: str) -> "UserModel":
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email: str) -> "UserModel":
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_id(cls, _id: int) -> "UserModel":
        return cls.query.filter_by(id=_id).first()

    def send_confirmation_email(self) -> Response:
        link = request.url_root[:-1] + url_for(
            "activation", activation_id=self.most_recent_activation.id
        )
        subject = "Registration activation"
        text = f"Please click the link to activate your registration: {link}"
        html = f'<html>Please click the link to activate your registration: <a href="{link}">Activation Link</a></html>'

        return Mailgun.send_email(self.email, subject, text, html)

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

    def verify_password(self, password: str) -> bool:
        return bc.check_password_hash(self.password, password)
