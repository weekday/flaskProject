#coding:utf-8

from . import main
from flask import render_template

@main.app_errorhandler(403)
def page_not_fount(e):
    return render_template('403.html'),403

@main.app_errorhandler(404)
def page_not_fount(e):
    return render_template('404.html'),404

@main.app_errorhandler(500)
def Internel_server_error(e):
    return render_template('500.html'),500