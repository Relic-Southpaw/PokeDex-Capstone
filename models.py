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
    team_name = db.Column(db.Text, nullable=False)
    pokemon1 = db.Column(db.Integer, nullable = False) 
    pokemon2 = db.Column(db.Integer, nullable = False)
    pokemon3 = db.Column(db.Integer, nullable = False)
    pokemon4 = db.Column(db.Integer, nullable = False)
    pokemon5 = db.Column(db.Integer, nullable = False)
    pokemon6 = db.Column(db.Integer, nullable = False)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainers.id'))

    user = db.relationship('User', backref="poketeams")

class PokeFav(db.Model):
    __tablename__ = 'favorite_pokemon'
    
    id = db.Column(
        db.Integer, 
        primary_key=True, 
        autoincrement=True
        )
    
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('trainers.id', ondelete='cascade')
    )

    poke_id = db.Column(
        db.Integer
    )

    @classmethod
    def addfavlist(cls, user_id, poke_id):
        """adds a favorite to the database tied to a user id"""

        pk_favorite = (
            user_id == user_id,
            poke_id == poke_id
        )
        db.session.add(pk_favorite)
        return pk_favorite

class User(db.Model):

    __tablename__ = 'trainers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    username = db.Column(db.Text, nullable=False,  unique=True)

    email = db.Column(db.Text, nullable = False, unique = True)

    password = db.Column(db.Text, nullable=False)

    favorite_pokemon = db.Column(db.Integer)

    favorites = db.relationship(
        'PokeFav'
    )

    @classmethod
    def signup(cls, username, email, password):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False
    

