from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,SubmitField
from wtforms.validators import InputRequired, Length , EqualTo,ValidationError
from models import Users
from passlib.hash import pbkdf2_sha256

def invalid_credentials(form,field):
    username_entered = form.username.data
    password_entered=field.data
    user=Users.query.filter_by(username=username_entered).first()
    if user is None:
        raise ValidationError('Username or Password is incorrect')
    elif not pbkdf2_sha256.verify(password_entered,user.password):
        raise ValidationError('Username Or Password is incorrect')

class RegistrationForm(FlaskForm):
    """Registration Form"""
    username=StringField('username_label',validators=[InputRequired("Username Required"),Length(min=4,max=25,message="Username should be between 4 and 25 characters")])
    password = PasswordField('password_label',validators=[InputRequired("Password Required"),Length(min=4,max=25,message="Password should be between 4 and 25 characters")])
    confirm_password = PasswordField('cpassword_label',validators=[InputRequired("Please Confirm Your Password"),EqualTo('password',message="Passwords Must match")])
    submit_btn=SubmitField("create")

    def validate_username(self,username):
        user_obj=Users.query.filter_by(username=username.data).first()
        if user_obj!=None:
            raise ValidationError("Username already taken. take another plzzzzz")


class LoginForm(FlaskForm):
    """Login Form"""
    username=StringField('username_label',validators=[InputRequired("Username Required")])
    password=PasswordField('password_label',validators=[InputRequired("Password Required"),invalid_credentials])
    submit_btn=SubmitField("login")



    
