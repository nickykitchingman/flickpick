from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, DateField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Email


class RegisterForm(FlaskForm):
    forename = StringField('First Name', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(),
                                                     EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = PasswordField(
        'Confirm Password', validators=[DataRequired()])

    birthday = DateField('Birthday', format="%d/%m/%Y",
                         validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    errors = []
