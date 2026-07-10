from flask import Blueprint, jsonify

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for the API."""
    return jsonify(
        {
            "status": "ok",
            "service": "open-research-repository-api",
        }
    )
