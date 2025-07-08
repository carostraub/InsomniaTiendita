from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Client

def admin_required(f):
    @wraps(f)
    @jwt_required()
    def wrapper (*args, **kwargs):
        current_user_id =get_jwt_identity
        user = Client.query.get(current_user_id)

        if not user or not user.is_admin:
            return jsonify ({"error":"Acceso denegado, tienes que ser administrador"}), 400
        return f(*args, **kwargs)
    return wrapper