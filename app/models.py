from app import db, errorLogger
from werkzeug.security import generate_password_hash
from flask_security import UserMixin, RoleMixin
from datetime import datetime

movie_choice = db.Table('movie_choice', db.Model.metadata,
    db.Column('userId', db.Integer, db.ForeignKey('user.userId')),
    db.Column('movieId', db.Integer, db.ForeignKey('movie.movieId')),
    db.Column('strength', db.Integer, index=True)
)

stream = db.Table('stream', db.Model.metadata,
    db.Column('movieId', db.Integer, db.ForeignKey('movie.movieId')),
    db.Column('streamSiteId', db.Integer, db.ForeignKey('stream_site.streamSiteId'))
)

user_site = db.Table('user_site', db.Model.metadata,
    db.Column('userId', db.Integer, db.ForeignKey('user.userId')),
    db.Column('streamSiteId', db.Integer, db.ForeignKey('stream_site.streamSiteId'))
)

in_group = db.Table('in_group', db.Model.metadata,
    db.Column('userId', db.Integer, db.ForeignKey('user.userId')),
    db.Column('groupId', db.Integer, db.ForeignKey('group.groupId'))
)

friendship = db.Table('friend', db.Model.metadata,
    db.Column('userId', db.Integer, db.ForeignKey('user.userId'), index=True),
    db.Column('friendId', db.Integer, db.ForeignKey('user.userId')),
    db.UniqueConstraint('userId', 'friendId', name='unique_friendships')
)

request = db.Table('request', db.Model.metadata,
    db.Column('userId', db.Integer, db.ForeignKey('user.userId'), index=True),
    db.Column('friendId', db.Integer, db.ForeignKey('user.userId')),
    db.Column('date', db.DateTime, nullable=False, default=datetime.now()),
    db.UniqueConstraint('userId', 'friendId', name='unique_requests')
)

user_role = db.Table(
    'user_role',
    db.Column('user_id', db.Integer, db.ForeignKey('user.userId')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.roleId'))
)

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
        primaryjoin=userId==friendship.c.userId,
        secondaryjoin=userId==friendship.c.friendId)
    requests = db.relationship('User', secondary=request,
        primaryjoin=userId==request.c.userId,
        secondaryjoin=userId==request.c.friendId)
    movies = db.relationship('Movie', secondary=movie_choice,
        backref=db.backref('user', lazy='joined'))
    streamSites = db.relationship("StreamSite", secondary=user_site,
        backref=db.backref('user', lazy='joined'))
    groups = db.relationship('Group', secondary=in_group,
        backref=db.backref('user', lazy='joined'))
    roles = db.relationship('Role', secondary=user_role,
        backref=db.backref('user', lazy='dynamic'))

    def set_password(self, password):
        self.password = generate_password_hash(password)

    # Simpler role interface
    def has_role(self, role):
        return role in [role.name for role in self.roles]
    def add_role(self, role):
        role_object = Role.query.filter_by(name=role).first()
        if role_object is None:
            errorLogger.error(f'Attempted to add role ({role}) that does not exist')
            return

        # Add role if exists and is not already assigned 
        if role_object not in self.roles:
            self.roles.append(role_object)
            db.session.commit()

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
    streamSites = db.relationship("StreamSite", secondary=stream,
        backref=db.backref('movie', lazy='joined'))

    def __repr__(self):
            return '{}{}{}'.format(self.movieId, self.name, self.releasedate)

class StreamSite(db.Model):
    streamSiteId = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))

    def __repr__(self):
            return '{}{}'.format(self.streamSiteId, self.name)

class Group(db.Model):
    groupId = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))

    def __repr__(self):
            return '{}{}'.format(self.groupId, self.name)

