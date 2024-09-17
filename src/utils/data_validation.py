from marshmallow import Schema, fields, validate, ValidationError, validates, validates_schema
from config import UserConfig, PollConfig
import re


class UserRegistrationSchema(Schema):
    first_name = fields.Str(required=True, validate=validate.Length(max=UserConfig.MAX_STRING_LENGTH))
    surname = fields.Str(required=True, validate=validate.Length(max=UserConfig.MAX_STRING_LENGTH))
    father_name = fields.Str(validate=validate.Length(max=UserConfig.MAX_STRING_LENGTH), allow_none=True,
                             missing=None)
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=UserConfig.MIN_PASSWORD_LENGTH))

    @validates('password')
    def validate_password(self, value):
        # Проверяем, содержит ли пароль хотя бы одну заглавную букву и один спецсимвол
        if not re.search(r'[A-Z]', value) or not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValidationError("Пароль должен содержить как минимум один специальный символ и "
                                  "одну букву в верхнем регистре.")


class PollCreationSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(max=PollConfig.DEFAULT_MAX_NAME_LENGTH))
    is_multiple_choice = fields.Boolean(missing=False)
    description = fields.Str(validate=validate.Length(max=PollConfig.DEFAULT_DECRIPTION_LENGTH), allow_none=True)
    is_temporary = fields.Boolean(missing=False)
    started_at = fields.DateTime(allow_none=True)
    finished_at = fields.DateTime(allow_none=True)
    option1 = fields.Str(validate=validate.Length(min=PollConfig.OPTION_LENGTH_MIN, max=PollConfig.OPTION_LENGTH_MAX),
                         allow_none=False)
    option2 = fields.Str(validate=validate.Length(min=PollConfig.OPTION_LENGTH_MIN, max=PollConfig.OPTION_LENGTH_MAX),
                         allow_none=False)
    option3 = fields.Str(validate=validate.Length(min=PollConfig.OPTION_LENGTH_MIN, max=PollConfig.OPTION_LENGTH_MAX),
                         allow_none=False)
    option4 = fields.Str(validate=validate.Length(min=PollConfig.OPTION_LENGTH_MIN, max=PollConfig.OPTION_LENGTH_MAX),
                         allow_none=False)
    option5 = fields.Str(validate=validate.Length(min=PollConfig.OPTION_LENGTH_MIN, max=PollConfig.OPTION_LENGTH_MAX),
                         allow_none=False)

    @validates_schema
    def validate_dates(self, data, **kwargs):
        if data.get("started_at") and data.get("finished_at"):
            if data["started_at"] >= data["finished_at"]:
                raise ValidationError("Дата окончания должна быть позже даты начала.")


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
