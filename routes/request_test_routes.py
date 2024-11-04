from flask import jsonify, request
from utils.request import make_response

def request_test_route(app):
    @app.route('/test', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
    def test_requests():
        # 返回当前请求的方法类型
        return make_response("request_type:"+request.method,200)
