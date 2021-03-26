
from time import time
from uuid import uuid4

from libs.db import db

ACTIVATION_EXPIRATION_DELTA = 1800  # 3 MINUTES


class ActivationModel(db.Model):
    __tablename__ = "activations"

    id = db.Column(db.String(50), primary_key=True)
    expire_at = db.Column(db.Integer, nullable=False)
    activated = db.Column(db.Boolean, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey(
        "users.id"), nullable=False)
    user = db.relationship("UserModel", viewonly=True)

    def __init__(self, user_id: int, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.id = uuid4().hex
        self.expire_at = int(time()) + ACTIVATION_EXPIRATION_DELTA
        self.activated = False

    @classmethod
    def find_by_id(cls, _id: str) -> "ActivationModel":
        return cls.query.filter_by(id=_id).first()

    @property
    def expired(self) -> bool:
        return time() > self.expire_at

    def force_to_expire(self) -> None:
        if not self.expired:
            self.expire_at = int(time())
            self.save_to_db()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
