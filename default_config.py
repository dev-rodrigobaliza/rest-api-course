import os

DEBUG = True
PORT = 5000

APP_NAME = "Stores REST API"

SECRET_KEY = os.environ.get("APP_SECRET_KEY", "App_-_s3CR3t_-_k3y")

JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jWt_-_s3CR3t_-_k3y")
JWT_BLOCKLIST_ENABLED = True
JWT_BLOCKLIST_TOKEN_CHECKS = ["access", "refresh"]

SQLALCHEMY_DATABASE_URI = "sqlite:///data.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False
PROPAGATE_EXCEPTIONS = True

FROM_EMAIL = "postmaster@sandboxb9fd6444809247b7bd7f631ef7fd28c5.mailgun.org"

UPLOADED_IMAGES_DEST = os.path.join("static", "images")
