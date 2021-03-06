from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from lsts.models import User
import email_validator
from flask_login import current_user


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=20)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    conf_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.query.filter(User.username.ilike(username.data)).first()
        if user:
            raise ValidationError(
                "That username is already in use. Please try another."
            )

    def validate_email(self, email):
        user = User.query.filter(User.email.ilike(email.data)).first()
        if user:
            raise ValidationError("That email is already in use. Please try another.")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


class UpdateAccountForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=20)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Update Now")

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter(User.username.ilike(username.data)).first()
            if user:
                raise ValidationError(
                    "That username is already in use. Please try another."
                )

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter(User.email.ilike(email.data)).first()
            if user:
                raise ValidationError(
                    "That email is already in use. Please try another."
                )


class AddItemForm(FlaskForm):
    item_name = StringField("Item Name", validators=[DataRequired()])
    category = StringField("Category")
    note = StringField("Note/Details")
    submit = SubmitField("Add Now")


class AddListForm(FlaskForm):
    list_name = StringField("List Name", validators=[DataRequired()])
    submit = SubmitField("Add Now")


class EditItemForm(FlaskForm):
    item_name = StringField("Item Name", validators=[DataRequired()])
    category = StringField("Category")
    note = StringField("Note/Details")
    submit = SubmitField("Update Item")


class EditListForm(FlaskForm):
    list_name = StringField("List Name", validators=[DataRequired()])
    submit = SubmitField("Update List")


class ResetRequestForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("New Password", validators=[DataRequired()])
    conf_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Change Password")
