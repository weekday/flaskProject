#coding:utf-8

from .. import db
from . import main
from .forms import NameForm
from datetime import datetime
from ..models import User
from ..email import send_mail
from flask import render_template,redirect,session,url_for,current_app

@main.route('/',methods=['GET','POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
            if current_app.config['FLASK_ADMIN']:
                send_mail(current_app.config['FLASK_ADMIN'],'New user','mail/new_user',user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        return redirect(url_for('.index'))
    return render_template('index.html',form=form,name=session.get('name'),
                           known=session.get('known',False))



