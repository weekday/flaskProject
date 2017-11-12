#coding:utf-8

from .. import db
from . import main
from .forms import NameForm
from datetime import datetime
from ..models import User
from ..email import send_mail
from flask import render_template,redirect,session,url_for,current_app

@main.route('/')
def index():
    return render_template('index.html')



