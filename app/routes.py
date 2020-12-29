from flask import Blueprint
from flask_restful import Api
from app.resources.auth import CaptchaResource, WsResource


urls = Blueprint('urls', __name__)

api = Api(urls)


api.add_resource(CaptchaResource, '/captcha')
api.add_resource(WsResource, '/ws')

