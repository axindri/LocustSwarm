from logging import getLogger

from flask import Flask, jsonify
from pydantic import ValidationError

from models.errors import ErrorResponse

logger = getLogger(__name__)


def create_exception_handlers(app: Flask) -> Flask:
    @app.errorhandler(500)
    def internal_error(error):
        logger.error("Internal server error: %s", error)
        return jsonify(
            ErrorResponse(
                error="Unhandled exception",
                message=f"Error {str(error)}",
                status_code=500,
            ).model_dump()
        ), 500

    @app.errorhandler(404)
    def not_found(error):
        return jsonify(
            ErrorResponse(
                error="Not found",
                message=f"Error {str(error)}",
                status_code=404,
            ).model_dump()
        ), 404

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        return jsonify(
            ErrorResponse(error="ValidationError", message=str(error), status_code=400).model_dump(),
        ), 422

    @app.errorhandler(ValueError)
    def handle_value_error(error):
        return jsonify(
            ErrorResponse(error="ValueError", message=str(error), status_code=400).model_dump(),
        ), 400

    @app.errorhandler(Exception)
    def handle_all_exceptions(error):
        logger.error("Unhandled exception: %s", error)
        return jsonify(
            ErrorResponse(
                error="Unhandled exception",
                message=f"Error {str(error)}",
                status_code=500,
            ).model_dump()
        ), 500

    return app


def set_config(app: Flask):
    app.config["JSON_AS_ASCII"] = False
    app.config["JSON_SORT_KEYS"] = False
    app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
    return app
