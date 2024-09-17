from flask import Flask
from flask_mail import Mail
from config import FlaskAppConfig, FlaskMailConfig
from models import db
from src.controllers.errors_controller import errorsBlueprint
from src.controllers.user.authentication_controller import registration_blueprint
from src.controllers.user.authentication_controller import login_blueprint
from src.controllers.user.authentication_controller import logout_blueprint
from src.controllers.poll.voting_controller import poll_blueprint
from src.controllers.poll.voting_controller import list_polls_blueprint

mail = Mail()
app = Flask(__name__)
app.config.from_object(FlaskAppConfig)
app.config['SECRET_KEY'] = app.config['APP_SECRET_KEY']
app.config['SECURITY_PASSWORD_SALT'] = FlaskMailConfig.SECURITY_PASSWORD_SALT
app.config['UPLOAD_FOLDER'] = app.config['UPLOAD_FOLDER']


mail.init_app(app)
db.init_app(app)

app.register_blueprint(registration_blueprint)
app.register_blueprint(login_blueprint)
app.register_blueprint(errorsBlueprint)
app.register_blueprint(logout_blueprint)
app.register_blueprint(poll_blueprint)
app.register_blueprint(list_polls_blueprint)


def create_db():
    with app.app_context():
        db.create_all()


if __name__ == '__main__':
    from models import *
    create_db()
    app.run(debug=True)
