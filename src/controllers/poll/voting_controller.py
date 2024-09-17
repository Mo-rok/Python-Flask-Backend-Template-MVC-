from src.utils.data_validation import PollCreationSchema, allowed_file
from flask import Blueprint, request, jsonify, session, current_app
from models import db, Poll, User, PollOption
from werkzeug.utils import secure_filename
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
from config import PollConfig
from uuid import uuid4
import os

poll_blueprint = Blueprint('poll_blueprint', __name__)
list_polls_blueprint = Blueprint('list_polls_blueprint', __name__)
vote_blueprint = Blueprint('vote', __name__)


@poll_blueprint.route('/create_poll', methods=['POST'])
def create_poll():
    if 'user_id' not in session:
        return jsonify({'message': 'Пользователь не авторизован'}), 401

    user_id = session['user_id']
    user = User.query.get(user_id)

    if not user:
        return jsonify({'message': 'Пользователь не найден'}), 404

    if not user.is_email_confirmed:
        return jsonify({'message': 'Аккаунт пользователя не подтвержден. Пожалуйста, подтвердите ваш email.'}), 403

    schema = PollCreationSchema()  # Экземпляр класса Schema для проверки полей голосования, вводимых юзером
    try:
        # Валидация текстовых данных
        data = schema.load(request.form.to_dict())

        # Получаем файл изображения
        image = request.files.get('image')
        if image and allowed_file(image.filename):
            if image.content_length > PollConfig.DEFAULT_MAX_IMAGE_SIZE:
                return jsonify(
                    {'message': f'Размер файла превышает максимально допустимый размер '
                                f'{PollConfig.DEFAULT_MAX_IMAGE_SIZE} байт'}), 400
            # Извлекаем расширение файла
            _, file_extension = os.path.splitext(image.filename)
            # Генерируем новое имя файла, используя только hex-строку и расширение
            filename = secure_filename(f"{uuid4().hex}{file_extension}")
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
            image_url = image_path  # Используем этот URL для сохранения в базе данных
        else:
            return jsonify({'message': 'Файл изображения не разрешен или отсутствует'}), 400

        options = [request.form.get(f'option{i}') for i in range(1, 6)]  # Получаем до 5 опций
        options = list(filter(None, options))  # Убираем пустые значения

        is_multiple_choice = data['is_multiple_choice']

        if is_multiple_choice:
            if not options or len(options) > 5:
                return jsonify({'message': 'Для множественного выбора нужно предоставить от 1 до 5 опций.'}), 400
        else:
            if len(options) < 2:
                # В случае, если is_multiple_choice=False, то запрашиваем минимум две опции (должен же быть выбор)
                return jsonify({'message': 'Для одиночного выбора нужно предоставить как минимум две опции.'}), 400

        # Проверяем, является ли голосование временным
        is_temporary = data['is_temporary']
        if not is_temporary:
            # Если голосование не является временным, игнорируем переданные значения для started_at и finished_at
            started_at = None
            finished_at = None
        else:
            # Если голосование временное, используем переданные значения
            started_at = data.get('started_at')
            finished_at = data.get('finished_at')

        # Создаем новый объект Poll
        new_poll = Poll(
            name=data['name'],
            is_multiple_choice=data['is_multiple_choice'],
            creator_id=user.id,
            is_moderated=False,  # Значение по умолчанию
            image_url=image_url,
            description=data.get('description', ''),
            is_rejected=False,  # Значение по умолчанию
            is_temporary=is_temporary,
            started_at=started_at,  # Значение зависит от is_temporary
            finished_at=finished_at  # Значение зависит от is_temporary
        )

        db.session.add(new_poll)
        db.session.flush()  # Требуется для получения ID нового голосования

        # Добавляем опции голосования в PollOption
        for option_title in options:
            new_option = PollOption(poll_id=new_poll.id, title=option_title)
            db.session.add(new_option)

        db.session.commit()

        return jsonify({'message': 'Голосование успешно создано'}), 201

    except ValidationError as err:
        # Возвращаем ошибки валидации
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({'message': f'Ошибка при создании голосования: {str(e)}'}), 500


@list_polls_blueprint.route('/polls', methods=['GET'])
def get_polls():
    try:
        page = max(request.args.get('page', 1, type=int), 1)  # Убедимся, что номер страницы не меньше 1
        per_page = request.args.get('per_page', 20, type=int)
        per_page = max(min(per_page, 100), 1)  # Ограничиваем размер страницы от 1 до 100

        polls_pagination = Poll.query.paginate(page=page, per_page=per_page, error_out=False)

        polls = [{
            'id': poll.id,
            'name': poll.name,
            'is_multiple_choice': poll.is_multiple_choice,
            'creator_id': poll.creator_id,
            'is_moderated': poll.is_moderated,
            'image_url': poll.image_url,
            'description': poll.description,
            'is_rejected': poll.is_rejected,
            'is_temporary': poll.is_temporary,
            'started_at': poll.started_at.isoformat() if poll.started_at else None,
            'finished_at': poll.finished_at.isoformat() if poll.finished_at else None,
        } for poll in polls_pagination.items]

        return jsonify({
            'polls': polls,
            'total': polls_pagination.total,
            'pages': polls_pagination.pages,
            'current_page': page
        }), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500


@vote_blueprint.route('/vote', methods=['POST'])
def vote():
    pass
