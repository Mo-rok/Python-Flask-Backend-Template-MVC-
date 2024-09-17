import logging
from flask import current_app
from src.crypto.hash import hashing, compare_hashes
from flask import Blueprint, request, jsonify, session
from models import db, User
from sqlalchemy.exc import SQLAlchemyError
from src.utils.data_validation import UserRegistrationSchema
from src.utils.email_utils.email_verifier import generate_confirmation_token, send_confirmation_email, confirm_token

# Настройка логгера
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Создаем Blueprint-ов для регистрации, авторизации и выхода из аккаунта
registration_blueprint = Blueprint('registrationBlueprint', __name__)
login_blueprint = Blueprint('loginBlueprint', __name__)
logout_blueprint = Blueprint('logoutBlueprint', __name__)


# Endpoint для регистрации
@registration_blueprint.route('/registration', methods=['POST'])
def registration():
    try:
        request_data = request.get_json()

        # Валидация данных
        errors = UserRegistrationSchema().validate(request_data)
        if errors:
            return jsonify(errors), 400

        validated_data = UserRegistrationSchema().load(request_data)

        # Проверка на существование пользователя по email
        user = User.query.filter(User.email == validated_data['email']).first()
        if user:
            return jsonify({'message': 'Пользователь уже существует'}), 409

        # Хеширование пароля
        hashed_password = hashing(validated_data['password'])

        new_user = User(first_name=validated_data['first_name'],
                        surname=validated_data['surname'],
                        father_name=validated_data.get('father_name'),
                        email=validated_data['email'],
                        password=hashed_password.decode('utf-8'))  # Сохраняем декодированный хеш пароля

        db.session.add(new_user)  # Добавляем нового пользователя в сессию
        db.session.commit()  # Сохраняем изменения в базе данных

        token = generate_confirmation_token(validated_data['email'])
        new_user.email_confirm_token = token
        db.session.commit()
        # send_confirmation_email(validated_data['email'], token)
        print(token)

        return jsonify({'message': 'Пользователь успешно создан'}), 201
    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy Error: {e}")
        return jsonify({'message': 'Неизвестная ошибка'}), 500  # Ошибка БД, но не сообщаем об этом пользователю явно
    except Exception as e:
        logger.error(f"General Error: {e}")
        return jsonify({'message': 'Ошибка обработки запроса'}), 500


@registration_blueprint.route('/confirm/<token>', methods=['GET'])
def confirm_email(token):
    try:
        email = confirm_token(token)
        if not email:
            # Если confirm_token вернул False, значит токен неверен или истек
            user = User.query.filter_by(email_confirm_token=token).first()  # Вытаскиваем инфу по пользователю на основании истекшего токена
            if user:
                new_token = generate_confirmation_token(user.email)
                print(new_token)
                user.email_confirm_token = new_token
                db.session.commit()
                send_confirmation_email(user.email, new_token)
                return jsonify({'message': 'Неверная ссылка подтверждения или время действия ссылки истекло. '
                                           'На вашу почту отправлена новая ссылка для подтверждения.'}), 400
            else:
                return jsonify({'message': 'Пользователь не найден.'}), 404

        user = User.query.filter_by(email=email).first_or_404()

        if user.is_email_confirmed:
            return jsonify({'message': 'Аккаунт уже был подтвержден'}), 200
        else:
            user.is_email_confirmed = True
            db.session.commit()
            return jsonify({'message': 'Вы успешно подтвердили вашу почту'}), 200

    except Exception as e:
        # Логирование любых других ошибок
        current_app.logger.error(f'Ошибка при подтверждении email: {e}')
        return jsonify({'message': 'Внутренняя ошибка сервера'}), 500


# Endpoint для авторизации
@login_blueprint.route('/login', methods=['POST'])
def login():
    try:
        request_data = request.get_json()
        email = request_data.get('email')
        password = request_data.get('password')

        if not email or not password:
            return jsonify({'message': 'Необходимо указать email и пароль'}), 400

        user = User.query.filter_by(email=email).first()

        if not user or not compare_hashes(password.encode('utf-8'), user.password.encode('utf-8')):
            return jsonify({'message': 'Неверный email или пароль'}), 401

        # Устанавливаем user_id в сессии после успешной аутентификации
        session['user_id'] = user.id

        return jsonify({'message': 'Успешная авторизация'}), 200

    except Exception as e:
        logger.error(f"General Error: {e}")
        return jsonify({'message': 'Ошибка обработки запроса'}), 500


# Endpoint для выхода из учетной записи
@logout_blueprint.route('/logout', methods=['POST'])
def logout():
    # Удаляем user_id из сессии для выхода пользователя
    session.pop('user_id', None)
    return jsonify({'message': 'Вы успешно вышли из системы'}), 200
