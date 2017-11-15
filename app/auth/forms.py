#coding:utf-8

from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import DataRequired,Length,Email,Regexp,EqualTo
from wtforms import ValidationError
from ..models import User

class RegistrationForm(FlaskForm):
    email = StringField(u'邮箱',validators=[DataRequired(),Length(1,64),Email()])
    username = StringField(u'用户名',validators=[DataRequired(),Length(1,64),
                Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,
                       u'用户名必须以字母开头，由字母、数字、点或下划线组成')])
    password = PasswordField(u'设置密码',validators=[DataRequired(),EqualTo('password2',message='Passwords must be match.')])
    password2 = PasswordField(u'确认密码',validators=[DataRequired()])
    submit = SubmitField(u'立即注册')

    def validate_email(self,field):
        if User.query.filter_by(email = field.data).first():
            raise ValidationError(u'该邮箱已被注册！')

    def validate_username(self,field):
        if User.query.filter_by(username = field.data).first():
            raise ValidationError(u'该用户名已被使用！')

#登录表单
class LoginForm(FlaskForm):
    email = StringField(u'邮箱',validators=[DataRequired(),Length(1,64),Email()])
    password = PasswordField(u'密码',validators=[DataRequired()])
    remember_me = BooleanField(u'记住我')
    submit = SubmitField(u'登录')


#修改密码表单
class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(u'旧密码',validators=[DataRequired()])
    password = PasswordField(u'请输入新密码',validators=[DataRequired(),EqualTo('password2',message='Passwords must be match.')])
    password2 = PasswordField(u'确认新密码',validators=[DataRequired()])
    submit = SubmitField(u'修改密码')

#重设密码邮箱验证
class PasswordResetRequestForm(FlaskForm):
    email = StringField(u'邮箱',validators=[DataRequired(),Length(1,64),Email()])
    submit = SubmitField(u'确定')

#重设密码表单
class PasswordResetForm(FlaskForm):
    email = StringField(u'邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField(u'输入密码',validators=[DataRequired(),EqualTo('password2',message='Passwords must be match.')])
    password2 = PasswordField(u'确认密码',validators=[DataRequired()])
    submit = SubmitField(u'重设密码')

    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Unknown email address')


#修改邮箱表单
class ChangeEmailForm(FlaskForm):
    email = StringField(u'新邮箱',validators=[DataRequired(),Length(1,64),Email()])
    password = PasswordField(u'密码',validators=[DataRequired()])
    submit = SubmitField(u'修改邮箱地址')

    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')

