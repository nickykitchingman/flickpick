from app import db, errorLogger, traceLogger

from werkzeug.security import generate_password_hash

from datetime import datetime
import random

in_group = db.Table('in_group', db.Model.metadata,
                    db.Column('userId', db.Integer,
                              db.ForeignKey('user.userId'), primary_key=True),
                    db.Column('groupId', db.Integer,
                              db.ForeignKey('group.groupId'), primary_key=True)
                    )

friendship = db.Table('friend', db.Model.metadata,
                      db.Column('userId', db.Integer, db.ForeignKey(
                          'user.userId'), index=True),
                      db.Column('friendId', db.Integer,
                                db.ForeignKey('user.userId')),
                      db.UniqueConstraint(
                          'userId', 'friendId', name='unique_friendships')
                      )

friend_request = db.Table('request', db.Model.metadata,
                          db.Column('userId', db.Integer, db.ForeignKey(
                              'user.userId'), index=True),
                          db.Column('friendId', db.Integer,
                                    db.ForeignKey('user.userId')),
                          db.Column('date', db.DateTime,
                                    nullable=False, default=datetime.now()),
                          db.UniqueConstraint(
                              'userId', 'friendId', name='unique_requests')
                          )

user_role = db.Table(
    'user_role',
    db.Column('user_id', db.Integer, db.ForeignKey(
        'user.userId'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey(
        'role.roleId'), primary_key=True)
)


class MovieChoice(db.Model):
    userId = db.Column(db.Integer,
                       db.ForeignKey('user.userId'), primary_key=True)
    movieId = db.Column(db.Integer,
                        db.ForeignKey('movie.movieId'), primary_key=True)
    strength = db.Column(db.Integer, index=True)

    def __repr__(self):
        return f"{self.userId}-{self.movieId}: {self.strength}"


class User(db.Model):
    userId = db.Column(db.Integer, primary_key=True)
    forename = db.Column(db.String(40))
    surname = db.Column(db.String(40))
    username = db.Column(db.String(40), unique=True)
    password = db.Column(db.String(200))
    birthday = db.Column(db.Date)
    email = db.Column(db.String(120), unique=True)

    # Relationships
    friends = db.relationship('User', secondary=friendship,
                              primaryjoin=userId == friendship.c.userId,
                              secondaryjoin=userId == friendship.c.friendId)
    requests = db.relationship('User', secondary=friend_request,
                               primaryjoin=userId == friend_request.c.userId,
                               secondaryjoin=userId == friend_request.c.friendId)
    moviechoices = db.relationship('Movie', secondary="movie_choice",
                                   backref=db.backref('users', lazy='joined'))
    groups = db.relationship('Group', secondary=in_group,
                             backref=db.backref('members', lazy='joined'))
    roles = db.relationship('Role', secondary=user_role,
                            backref=db.backref('users', lazy='dynamic'))

    # Hash password instead of saving plaintext
    def set_password(self, password):
        self.password = generate_password_hash(password)

    # Simpler role interface
    def has_role(self, role):
        return role in [role.name for role in self.roles]

    def add_role(self, role):
        role_object = Role.query.filter_by(name=role).first()
        if role_object is None:
            errorLogger.error(
                f'Attempted to add role ({role}) that does not exist')
            return

        # Add role if exists and is not already assigned
        if role_object not in self.roles:
            self.roles.append(role_object)
            db.session.commit()

    def in_group(self, name):
        return name in [group.name for group in self.groups]

    def in_group_id(self, id):
        return id in [str(group.groupId) for group in self.groups]

    def has_friend(self, username):
        return username in [friend.username for friend in self.friends]

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return '{}{}{}{}{}{}{}'.format(self.userId, self.forename, self.surname, self.username, self.password, self.birthday, self.email)


class Role(db.Model):
    roleId = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        return f"{self.name}: {self.description}"


class Movie(db.Model):
    movieId = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    releasedate = db.Column(db.Date)

    # Return a random movie
    def get_random(user_id):
        #query = Movie.query
        traceLogger.debug(f'Random: user ({user_id})')
        query = db.session.query(
            Movie).filter(~Movie.users.any(userId=user_id))
        num_movies = int(query.count())
        return query.offset(int(num_movies*random.random())).first()

    def niceDate(self):
        return self.releasedate.strftime('%b %d %Y')

    def as_dict(self):
        return {"movieId": self.movieId,
                "name": self.name,
                "releasedate": self.niceDate()}

    def __repr__(self):
        return '{}{}{}'.format(self.movieId, self.name, self.releasedate)


class Group(db.Model):
    groupId = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))

    def __repr__(self):
        return '{}{}'.format(self.groupId, self.name)
