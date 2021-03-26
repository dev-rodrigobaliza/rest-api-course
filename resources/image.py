import os
import traceback

from flask_restful import Resource
from flask_uploads import UploadNotAllowed
from flask import request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity

from libs import im
from libs.i18n import get_text
from schemas.image import ImageSchema

image_schema = ImageSchema()


class ImageUpload(Resource):
    @classmethod
    @jwt_required()
    def post(cls):
        """
        Upload an image file. It uses JWT to retrieve user information and then saves the image to the user's folder.
        If there is a filename conflict, it appends a number at the end.
        """
        data = image_schema.load(request.files)
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"

        try:
            image_path = im.save_image(data["image"], folder)
            basename = im.get_basename(image_path)

            return {"message": get_text("image_uploaded").format(basename)}, 201
        except UploadNotAllowed:
            extension = im.get_extension(data["image"])
            return {"message": get_text("image_extension_not_allowed").format(extension)}, 400


class Image(Resource):
    @classmethod
    @jwt_required()
    def get(cls, filename: str):
        """
        Returns the reuqested image if it exists. Looks inside the logged in user's folder.
        """
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"

        if not im.is_filename_safe(filename):
            return {"message": get_text("image_illegal_file_name").format(filename)}, 400

        try:
            return send_file(im.get_path(filename, folder))
        except FileNotFoundError:
            return {"message": get_text("image_not_found").format(filename)}, 404

    @classmethod
    @jwt_required()
    def delete(cls, filename: str):
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"

        if not im.is_filename_safe(filename):
            return {"message": get_text("image_illegal_file_name").format(filename)}, 400

        try:
            os.remove(im.get_path(filename, folder))
            return {"message": get_text("image_deleted").format(filename)}, 200
        except FileNotFoundError:
            return {"message": get_text("image_not_found").format(filename)}, 404
        except:
            traceback.print_exc()
            return {"message": get_text("image_delete_error").format(filename)}, 500


class AvatarUpload(Resource):
    @classmethod
    @jwt_required()
    def put(cls):
        """
        Upload user avatars. All avatars are named after the user's ID.
        Something like this: user_{id}.{ext}
        Uploading a new avatar overwrites the existing one.
        """
        data = image_schema.load(request.files)
        user_id = get_jwt_identity()
        filename = f"user_{user_id}"
        folder = "avatars"
        avatar_path = im.find_image_any_format(filename, folder)

        if avatar_path:
            try:
                os.remove(avatar_path)
            except:
                return {"message": get_text("avatar_delete_error").format(filename)}, 500

        try:
            ext = im.get_extension(data["image"].filename)
            name = filename + ext
            avatar_path = im.save_image(data["image"], folder, name)
            basename = im.get_basename(avatar_path)

            return {"message": get_text("avatar_uploaded").format(basename)}, 200
        except UploadNotAllowed:
            extension = im.get_extension(data["image"])
            return {"message": get_text("image_extension_not_allowed").format(extension)}, 400


class Avatar(Resource):
    @classmethod
    @jwt_required()
    def get(cls, user_id: int):
        filename = f"user_{user_id}"
        folder = "avatars"
        avatar = im.find_image_any_format(filename, folder)

        if avatar:
            return send_file(avatar)

        return {"message": get_text("avatar_not_found").format(user_id)}, 404
