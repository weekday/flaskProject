#coding:utf-8

from ..models import Role,User
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,TextAreaField,BooleanField,SelectField,ValidationError
from wtforms.validators import DataRequired,Length,Email,Regexp
from flask_pagedown.fields import PageDownField

class NameForm(FlaskForm):
    name = StringField('What is your name?',validators=[DataRequired()])
    submit = SubmitField(u'注册')


#普通用户资料编辑表单
class EditProfileForm(FlaskForm):
    name = StringField(u'姓名',validators=[Length(0,64)])
    location = StringField(u'通信地址',validators=[Length(0,128)])
    about_me = TextAreaField(u'自我介绍')
    submit = SubmitField(u'提交信息')

#管理员资料编辑表单
class EditProfileAdminForm(FlaskForm):
    email = StringField(u'邮箱',validators=[DataRequired(),Length(1,64),Email()])
    username = StringField(u'用户名',validators=[DataRequired(),Length(1,64),Regexp(
        '^[A-Za-z][A-Za-z0-9_.]*$',0,u'用户名必须以字母开头，由字母、数字、点或下划线组成')])
    confirmed = BooleanField(u'已验证')
    role = SelectField(u'角色',coerce=int)
    name = StringField(u'真实姓名',validators=[Length(0,64)])
    location = StringField(u'通信地址', validators=[Length(0, 128)])
    about_me = TextAreaField(u'自我介绍')
    submit = SubmitField(u'提交信息')

    def __init__(self,user,*args,**kwargs):
        super(EditProfileAdminForm,self).__init__(*args,**kwargs)
        self.role.choices = [(role.id,role.name) for role in Role.query.filter_by(Role.name).all()]
        self.user = user

    def validate_email(self,field):
        if field.email != self.user.email and User.query.filter_by(email=field.email):
            raise ValidationError(u'该邮箱已被注册！')

    def validate_username(self,field):
        if field.username !=self.user.username and User.query.filter_by(username=field.username):
            raise ValidationError(u'用户名已被使用！')

#博客文章表单
class PostForm(FlaskForm):
    body = PageDownField(u'您要发表什么内容？',validators=[DataRequired()])
    submit = SubmitField(u'提交内容')


