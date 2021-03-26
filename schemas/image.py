from marshmallow import Schema, fields
from werkzeug.datastructures import FileStorage

from libs.im import is_filename_safe


class FileStoragField(fields.Field):
    default_error_messages = {"invalid": "Not a valid image."}

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return None

        if not isinstance(value, FileStorage):
            self.fail("invalid")

        return value


class ImageSchema(Schema):
    image = FileStoragField(required=True)
