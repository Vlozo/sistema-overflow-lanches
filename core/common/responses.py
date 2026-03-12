
from flask import jsonify

def send_response(message, code):
    return jsonify({"message": str(message)}), code

def http_error(message, code):
    return jsonify({"error": str(message)}), code

def bad_request(message):
    return http_error(message, 400)

def forbidden(message = "Acesso negado"):
    return http_error(message, 403)