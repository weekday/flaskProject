#coding:utf-8

from . import auth
from .. import db
from ..email import  send_mail
from ..models import User
from .forms import LoginForm,RegistrationForm
from flask_login import login_required,login_user,current_user
from flask import render_template,redirect,request,url_for,flash

@auth.route('/register',methods = ['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email = form.email.data,username = form.username.data,password = form.password.data)
        db.session.add(user)
        db.session.commit()
        token = User.generate_confirmation_token()
        send_mail(user.email,'Confirm Your Account','auth/email/confirm',user=user,token=token)
        flash(u'已发送一封验证消息到您的邮箱')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html',form = form)

@auth.route('/login',methods = ['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me)
            return redirect(request.args.get('next')or url_for('main.index'))
        flash(u'用户名或密码无效')
    return render_template('auth/login.html',form = form)


@auth.route('/logout')
@login_required
def logout():
    login_user()
    flash(u'您已登出....')
    return redirect(url_for('main.index'))

#确认用户帐户
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    elif current_user.confirm(token):
        flash('You have confirmed your account.Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))


