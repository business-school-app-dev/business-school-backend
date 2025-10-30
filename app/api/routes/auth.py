from flask import Blueprint, jsonify, request

auth_bp = Blueprint("auth", __name__)

@auth_bp.post("/auth/register")
def register():
    # placeholder so the import works
    return jsonify({"ok": True})
