import functools

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from app import app, db, models, accessLogger
from .forms import RegisterForm, LoginForm
from .models import User, Movie

bp = Blueprint('auth', __name__, url_prefix='/auth')


def usernameExists(username):
    return db.session.query(User.userId).filter_by(username=username).first() is not None


def emailExists(email):
    return db.session.query(User.userId).filter_by(email=email).first() is not None


@bp.before_app_request
def load_logged_in_user():
    #session['user_id'] = 1
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter_by(userId=user_id).first()


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            accessLogger.info(
                'User attempted to access page whilst not logged in - returned to auth.login')
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            accessLogger.info(
                'User attempted to access admin page whilst not logged in - returned to auth.login')
            return redirect(url_for('auth.login'))

        if not g.user.has_role('superuser'):
            accessLogger.info(
                'User attempted to access admin page whilst admin - returned to auth.login')
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        # Validate username and email not already in use
        if (usernameExists(form.username.data)):
            form.username.errors.append('Username already taken')
        if (emailExists(form.email.data)):
            form.email.errors.append('Email already in use')
        else:
            # Create new user model
            u = User(forename=form.forename.data,
                     surname=form.surname.data,
                     username=form.username.data,
                     password=generate_password_hash(form.password.data),
                     birthday=form.birthday.data,
                     email=form.email.data)
            u.add_role('user')

            # Add new user to database
            db.session.add(u)
            db.session.commit()
            accessLogger.info(
                f'Registered (id:{u.userId}, username:{u.username})')
            return redirect(url_for('auth.login'))

    return render_template('auth/register.html',
                           user_level=0,
                           title='Register',
                           form=form)


@bp.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm()

    if form.validate_on_submit():
        # Retrieve user
        user = User.query.filter_by(username=form.username.data).first()

        # Clear errors
        form.errors.clear()

        # Username or password incorrect - not disclosing which
        if user is None or not check_password_hash(user.password, form.password.data):
            accessLogger.warning(f'Login FAIL (username:{form.username.data})')
            form.errors.append('Incorrect details')
        # Log user into session
        else:
            session.clear()
            session['user_id'] = user.userId
            accessLogger.info(
                f'Login SUCCESS (id:{user.userId}, username:{user.username})')
            return redirect(url_for('index'))

    return render_template('auth/login.html',
                           user_level=0,
                           title='Login',
                           form=form)


@bp.route('/logout')
def logout():
    # Logger
    userId = session.get('user_id')
    if userId is None:
        accessLogger.error(f'Logout NO ID')
    accessLogger.info(f'Logout (id:{userId})')

    # Clean and return to index
    session.clear()
    return redirect(url_for('index'))
