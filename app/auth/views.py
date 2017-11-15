#coding:utf-8

from . import auth
from .. import db
from ..email import send_mail
from ..models import User
from .forms import LoginForm,RegistrationForm,ChangeEmailForm,\
	ChangePasswordForm,PasswordResetForm,PasswordResetRequestForm
from flask_login import login_required,logout_user,current_user,login_user
from flask import render_template,redirect,request,url_for,flash

#注册账号
@auth.route('/register',methods = ['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email = form.email.data,
                    username = form.username.data,
                    password = form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_mail(user.email,'Confirm Your Account','auth/email/confirm',
                  user=user,token=token)
        flash(u'已发送一封验证消息到您的邮箱')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html',form = form)

#登录
@auth.route('/login',methods = ['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)
        flash(u'用户名或密码无效')
    return render_template('auth/login.html',form = form)

#登出
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash(u'您已登出....')
    return redirect(url_for('main.index'))

#确认用户帐户
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('You have confirmed your account.Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))

#过滤未确认的帐户
@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed and request.endpoint \
				and request.blueprint != 'auth' and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))

#重新发送帐户确认邮件
@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_mail(current_user.email,'Confirm Your Account',\
			  'auth/email/confirm',user = current_user,token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))


#修改密码
@auth.route('/change-password',methods=['GET','POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash(u'您的密码已经更新.')
            return redirect(url_for('main.index'))
        else:
            flash(u'无效密码.')
    return render_template('auth/change_password.html',form = form)

#重置密码请求
@auth.route('/reset',methods=['GET','POST'])
def password_reset_request():
	if not current_user.is_anonymous:
		return redirect(url_for('main.index'))
	form = PasswordResetRequestForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user:
			token = user.generate_reset_token()
			send_mail(user.email,u'重置您的密码','auth/email/reset_password',\
					  user=user,token=token,next=request.args.get('next'))
		flash(u'已为您的邮箱发送了一封重置密码的确认邮件.')
		return redirect(url_for('auth.login'))
	return render_template('auth/reset_password.html', form=form)

#重置密码
@auth.route('/reset/<token>',methods=['GET','POST'])
def password_reset(token):
	if not current_user.is_anonymous:
		return redirect(url_for('main.index'))
	form = PasswordResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user.reset_password(token,form.password.data):
			flash(u'您的密码已更新.')
			return redirect(url_for('auth.login'))
		else:
			return redirect(url_for('main.index'))
	return render_template('auth/reset_password.html', form=form)

#邮箱更改请求
@auth.route('/change-email',methods=['GET','POST'])
@login_required
def change_email_request():
	form = ChangeEmailForm()
	if form.validate_on_submit():
		if current_user.verify_password(form.password.data):
			new_email = form.email.data
			token = current_user.generate_email_change_token(new_email)
			send_mail(new_email,u'验证您的邮箱地址','auth/email/change_email',\
					  user = current_user,token = token)
			flash(u'已为您的新邮箱发送了一封验证邮件.')
			return redirect(url_for('main.index'))
		else:
			flash(u'邮箱或密码错误.')
	return render_template('auth/change_email.html',form=form)

@auth.route('/change-email/<token>',methods=['GET','POST'])
@login_required
def change_email(token):
	if current_user.chang_email(token):
		db.session.commit()
		flash(u'您的邮箱地址已经更新.')
	else:
		flash(u'请求无效.')
	return redirect(url_for('main.index'))

			

