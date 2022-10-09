from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, SearchField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField


class UserForm(FlaskForm):  # Create a Form Class:
    name = StringField("FIO:", validators=[DataRequired()])
    username = StringField("Login:", validators=[DataRequired()])
    email = StringField("E-mail:", validators=[DataRequired()])
    e = StringField("Comment:", validators=[DataRequired()])
    about_author = TextAreaField("Vrach haqida:", validators=[DataRequired()])
    password_hash = PasswordField("Password:", validators=[
                                  DataRequired(), EqualTo("password_hash2", message="Password'lar bir xil bo'lishi kerak!")])
    password_hash2 = PasswordField(
        "Confirm Password:", validators=[DataRequired()])
    profile_pic = FileField("Profile 📷")
    submit = SubmitField("Submit")


class NamerForm(FlaskForm):
    name = StringField("👨‍👩‍👦", validators=[DataRequired()])
    submit = SubmitField("Submit")


class PasswordForm(FlaskForm):
    email = StringField("✉", validators=[DataRequired()])
    password_hash = PasswordField("🔑", validators=[DataRequired()])
    submit = SubmitField("Submit")


class PostForm(FlaskForm):
    title = StringField("Mavzu:", validators=[DataRequired()])
    # content = StringField("🎮", validators=[DataRequired()], widget=TextArea())
    content = CKEditorField("Content", validators=[DataRequired()])
    author = StringField("👨🏻‍⚕️👩🏻‍⚕️")
    slug = StringField("🔗", validators=[DataRequired()])
    submit = SubmitField("OK")


class LoginForm(FlaskForm):
    username = StringField("Login", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("OK")


class SearchForm(FlaskForm):
    searched = StringField("Search", validators=[DataRequired()])
    # profile_pic = FileField("Profile pic.")
    submit = SubmitField("Submit")
