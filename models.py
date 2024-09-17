from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    surname = db.Column(db.String(80), nullable=False)
    father_name = db.Column(db.String(80), nullable=True)  # предполагаем, что отчество может быть не указано
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    is_email_confirmed = db.Column(db.Boolean, default=False)
    email_confirm_token = db.Column(db.String(100))


class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    is_multiple_choice = db.Column(db.Boolean, default=False, nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_moderated = db.Column(db.Boolean, default=False, nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_rejected = db.Column(db.Boolean, default=False, nullable=False)
    is_temporary = db.Column(db.Boolean, default=False, nullable=False)
    started_at = db.Column(db.DateTime, nullable=True)
    finished_at = db.Column(db.DateTime, nullable=True)
    is_limited_access = db.Column(db.Boolean, default=False)
    max_votes = db.Column(db.Integer, default=1000)

    # Связь с User (создатель голосования)
    creator = db.relationship('User', backref=db.backref('created_polls', lazy=True))


class PollOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)

    # Связь с Poll
    poll = db.relationship('Poll', backref=db.backref('options', lazy=True))


'''class PollUserMatch(db.Model):  # Нужна ли данная модель?
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'), nullable=False)
    option_id = db.Column(db.Integer, db.ForeignKey('poll_option.id'))

    # Связи
    user = db.relationship('User', backref=db.backref('votes', lazy=True))
    poll = db.relationship('Poll', backref=db.backref('user_votes', lazy=True))
    poll_option = db.relationship('PollOption', backref=db.backref('votes', lazy=True))'''
