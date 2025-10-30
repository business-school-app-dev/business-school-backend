from flask import Blueprint, jsonify

me_bp = Blueprint("me", __name__)

@me_bp.get("/me")
def me():
    return jsonify({"me": True})
