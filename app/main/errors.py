#coding:utf-8

from . import main
from flask import render_template, request, jsonify


@main.app_errorhandler(403)
def page_not_fount(e):
    if request.accept_mimetypes.accept_json and \
        not request.accept_mimetypes.accept_html:
        response = jsonify({'error':'forbbiden'})
        response.status_code = 403
        return response
    return render_template('403.html'),403

@main.app_errorhandler(404)
def page_not_fount(e):
    if request.accept_mimetypes.accept_json and \
        not request.accept_mimetypes.accept_html:
        response = jsonify({'error':'page not fount'})
        response.status_code = 404
        return response
    return render_template('404.html'),404

@main.app_errorhandler(500)
def Internel_server_error(e):
    if request.accept_mimetypes.accept_json and \
        not request.accept_mimetypes.accept_html:
        response = jsonify({'error':'internal server error'})
        response.status_code = 500
        return response
    return render_template('500.html'),500