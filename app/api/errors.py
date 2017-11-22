#coding:utf-8
from flask import jsonify
from ..exceptions import ValidationError
from . import api

def bad_request(message):
    response = jsonify({"error":"bad request","message":message})
    response.status_code = 400
    return response

def unauthorized(message):
    response = jsonify({"error":"unauthorized","message":message})
    response.status_code = 401
    return response

def forbidden(message):
    response = jsonify({"error":"forbidden","message":message})
    response.status_code = 403
    return response


#API中的ValidationError一场处理程序
@api.errorhandler(ValidationError)
def Validation_error(e):
    return bad_request(e.args[0])