#coding:utf-8

from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import DataRequired,Length,Email,Regexp,EqualTo
from wtforms import ValidationError
from ..models import User

class RegistrationForm(FlaskForm):
    email = StringField(u'邮箱',validators=[DataRequired(),Length(1,64),Email()])
    username = StringField(u'用户名',validators=[DataRequired(),Length(1,64),
                Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,'Usernames must have only letters,numbers,dots or underscores')])
    password = PasswordField(u'设置密码',validators=[DataRequired(),EqualTo('password2',message='Password must be match.')])
    password2 = PasswordField(u'确认密码',validators=[DataRequired()])
    submit = SubmitField(u'立即注册')

    def validate_email(self,field):
        if User.query.filter_by(email = field.data).first():
            raise ValidationError(u'该邮箱已被注册！')

    def validate_username(self,field):
        if User.query.filter_by(username = field.data).first():
            raise ValidationError(u'该用户名已被使用！')

class LoginForm(FlaskForm):
    email = StringField(u'邮箱',validators=[DataRequired(),Length(1,64),Email()])
    password = PasswordField(u'密码',validators=[DataRequired()])
    remember_me = BooleanField(u'记住我')
    submit = SubmitField(u'登录')

