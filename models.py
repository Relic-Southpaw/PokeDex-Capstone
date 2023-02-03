from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class PokeTeam(db.Model):
    __tablename__ = 'poketeams'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    team = db.Column(db.Text, nullable=False)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainers.id'))

    user = db.relationship('User', backref="poketeams")


class User(db.Model):

    __tablename__ = 'trainers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    username = db.Column(db.Text, nullable=False,  unique=True)

    email = db.Column(db.Text, nullable = False, unique = True)

    password = db.Column(db.Text, nullable=False)

    @classmethod
    def register(cls, username, pwd):
        """Register trainer w/hashed password & return trainer."""

        hashed = bcrypt.generate_password_hash(pwd)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        # return instance of trainer w/username and hashed pwd
        return cls(username=username, password=hashed_utf8)

    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that trainer exists & password is correct.

        Return trainer if valid; else return False.
        """

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, pwd):
            # return user instance
            return u
        else:
            return False
