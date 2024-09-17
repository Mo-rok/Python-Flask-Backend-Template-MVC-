from itsdangerous import URLSafeTimedSerializer as Serializer
from itsdangerous.exc import SignatureExpired, BadSignature  # Импорт исключений
from flask_mail import Message
from flask import current_app
from config import FlaskMailConfig, FlaskAppConfig


def generate_confirmation_token(email):
    serializer = Serializer(FlaskAppConfig.APP_SECRET_KEY)
    return serializer.dumps(email, salt=FlaskMailConfig.SECURITY_PASSWORD_SALT)


def send_confirmation_email(user_email, token):
    """
    mail пришлось реализовывать через экземпляр текущего приложения "current_app",
    т.к. инициализация и импорт Mail из main.py вызывает ошибку циклического импорта.
    Необходимо перепроверить все импорты, избавиться от ненужных. Возможно потребуется
    реализовать фабричный метод сборки приложения
    """
    mail = current_app.extensions['mail']

    confirm_url = f'http://127.0.0.1:5000/confirm/{token}'
    msg = Message('Подтвердите вашу почту', sender=FlaskMailConfig.SENDER, recipients=[user_email])
    msg.body = f'Пожалуйста, перейдите по ссылке для подтверждения вашей почты: {confirm_url}'
    mail.send(msg)


def confirm_token(token, max_age=120):  # 120 секунд = 2 минуты
    serializer = Serializer(FlaskAppConfig.APP_SECRET_KEY)
    try:
        email = serializer.loads(
            token,
            salt=current_app.config['SECURITY_PASSWORD_SALT'],
            max_age=max_age
        )
    except SignatureExpired:
        # Обработка случая, когда время жизни токена истекло
        return False
    except BadSignature:
        # Обработка случая неверной подписи токена
        return False
    return email
