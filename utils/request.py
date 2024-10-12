from flask import jsonify


def make_response(message, code, body=None):
    response = {
        'message': message,
        'code': code,
        'body': body
    }
    return jsonify(response), code
