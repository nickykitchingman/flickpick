from app import db
from werkzeug.security import generate_password_hash
from flask_security import UserMixin, RoleMixin

movie_choice = db.Table('movie_choice', db.Model.metadata,
    db.Column('userId', db.Integer, db.ForeignKey('user.userId')),
    db.Column('movieId', db.Integer, db.ForeignKey('movie.movieId'))
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

user_role = db.Table(
    'user_role',
    db.Column('user_id', db.Integer, db.ForeignKey('user.userId')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.roleId'))
)

class User(db.Model, UserMixin):
    userId = db.Column(db.Integer, primary_key=True)
    forename = db.Column(db.String(40))
    surname = db.Column(db.String(40))
    username = db.Column(db.String(40), unique=True)
    password = db.Column(db.String(200))
    birthday = db.Column(db.Date)
    email = db.Column(db.String(120), unique=True)

    # Relationships
    friends = db.relationship('User', secondary=friendship,
        backref='user',
        primaryjoin=userId==friendship.c.userId,
        secondaryjoin=userId==friendship.c.friendId)
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

    def has_role(self, role):
        return role in self.roles

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
            return '{}{}{}{}{}{}{}'.format(self.userId, self.forename, self.surname, self.username, self.password, self.birthday, self.email)

class Role(db.Model, RoleMixin):
    roleId = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        return self.name

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

