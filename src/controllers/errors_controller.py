from flask import Blueprint, jsonify

# Создаем новый Blueprint для обработчика ошибок
errorsBlueprint = Blueprint('errors', __name__)

# Этот обработчик перехватывает все 404 ошибки


@errorsBlueprint.app_errorhandler(404)
def notFoundError(error):
    return jsonify({'error': 'The resource was not found'}), 404

# Дополнительный обработчик для внутренних ошибок сервера (500)


@errorsBlueprint.app_errorhandler(500)
def internalError(error):
    # Здесь можно добавить логику логирования ошибок
    return jsonify({'error': 'Internal server error'}), 500
