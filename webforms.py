from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, SelectField,  TextAreaField, validators,
                     IntegerField, ValidationError,  SelectMultipleField, BooleanField)
from wtforms.validators import Length
from models import run_data

# login form


class LoginForm(FlaskForm):
    user_name = StringField('User name', validators=[Length(3, 10, message='Password - between 3-10 numbsers'),
                                                     validators.input_required()])
    password = StringField('Password', validators=[
        validators.input_required()])
    submit = SubmitField('Log In')

# register form


class RegisterForm(FlaskForm):

    def validate_student_id(self, student_id):
        sql = f"select student_id from student where student_id = '{student_id.data}'"
        result = run_data(sql, fetch=1)
        if result:
            raise ValidationError('Student ID exists')

    # define user_name validation function - to check if user_name exists
    def validate_user_name(self, user_name):
        sql = f"select * from user where user_name = '{user_name.data}'"
        result = run_data(sql, fetch=1)
        if result:
            raise ValidationError(
                'Username already exists, please try another one')

    def validate_email_exist(self, email):
        sql = f"select email from student where email = '{email.data}'"
        result = run_data(sql, fetch=1)
        if result:
            raise ValidationError('Email exists')

    student_id = StringField('Student ID', validators=[Length(min=4, max=4, message="not valided"),
                                                       validators.DataRequired(), validate_student_id])

    # add self-defined function to validate user_name within flask-wtf tool
    user_name = StringField('Username', validators=[
        validators.DataRequired(), validate_user_name])

    password = StringField('Password', validators=[Length(min=4),
                                                   validators.DataRequired()])

    first_name = StringField('First Name', validators=[
        validators.DataRequired()])

    last_name = StringField('Last Name', validators=[
        validators.DataRequired()])

    # delete preferred name validation as per Craig suggested
    preferred_name = StringField('Preferred Name')

    email = StringField('Email', validators=[
                        validators.DataRequired(), validators.Email(), validate_email_exist])

    phone = IntegerField('Phone', validators=[
        validators.DataRequired(message='Phone number must be between 1 and 12 digits in length')])

    location = SelectField('Location', choices=[
        ('Auckland', 'Auckland'), ('Wellington',
                                   'Wellington'), ('Hamilton', 'Hamilton'),
        ('Christchurch', 'Christchurch'), ('Other', 'Other')], validators=[validators.input_required()])
    # add skills field
    skills = SelectMultipleField('Skills', choices=[
        ('1', 'Python'), ('2', 'Javascript'), ('3', 'HTML/CSS'),
        ('4', 'Database/SQL'), ('5', 'User Experience'),
        ('6', 'UI Design'), ('7', 'Content Creation'),
        ('8', 'Business analysis'), ('9', 'GIS'),
        ('10', 'Neural neworks'), ('11', 'Node.js'),
        ('12', 'React.js'), ('13', 'Angular.js'),
    ], validators=[validators.input_required()])
    # ask student if have their own project
    need_project = SelectField('Need to be placed', choices=[
        ('1', 'Yes'), ('0', 'No')], validators=[validators.input_required()])

    currently_enrolled = SelectField('Currently Enrolled', choices=[('1', 'Yes'), ('0', 'No')],
                                     validators=[validators.input_required()])

    semester_to_place = SelectField('Semester to place', choices=[
        ('2', 'Semester 2'), ('1', 'Semester 1')], validators=[validators.input_required()])

    submit = SubmitField('Register')

# search form for user to search  out desired information


class SearchForm(FlaskForm):
    search = StringField('Search', validators=[
                         validators.input_required()])
    submit = SubmitField('Search')

# notice form for user to send notice to other


class NoticeForm(FlaskForm):
    subject = StringField('subject', validators=[validators.input_required()])
    send_to = StringField('send_to', validators=[validators.input_required()])
    message = TextAreaField('message', validators=[
                            validators.input_required()])

    send = SubmitField('send')
