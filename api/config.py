from logging import getLogger
from pathlib import Path

from flask import Blueprint, Response, request

from config.settings import settings
from models.config import Config

logger = getLogger(__name__)

bp = Blueprint("config", __name__, url_prefix="/api")


@bp.route("/config")
def get_config():
    return Response(
        settings.config.model_dump_json(
            ensure_ascii=False,
            indent=2,
        ),
        mimetype="application/json; charset=utf-8",
    )


@bp.route("/config", methods=["POST"])
def set_config():
    data = request.get_json()
    logger.debug("Got data %s", data)

    config = Config.model_validate(data)
    config_path = Path(settings.config_path)

    with open(config_path, "w", encoding="utf-8") as f:
        f.write(config.model_dump_json(indent=2))

    return config.model_dump_json()
