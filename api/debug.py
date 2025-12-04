from logging import getLogger

from flask import Blueprint, jsonify

from models.errors import ErrorResponse
from utils.docker import docker

logger = getLogger(__name__)

bp = Blueprint("debug", __name__, url_prefix="/api/debug")


@bp.route("/docker")
def debug_docker():
    try:
        all_containers = docker.get().containers.list(all=True)

        containers_info = []
        for container in all_containers:
            container_info = {
                "id": container.id[:12],
                "name": container.name,
                "status": container.status,
                "image": container.image.tags if container.image.tags else str(container.image),
                "created": container.attrs["Created"],
                "ports": container.ports,
            }
            containers_info.append(container_info)

        return jsonify({"total_containers": len(all_containers), "containers": containers_info})

    except Exception as e:
        return jsonify(
            ErrorResponse(
                status_code=500,
                message=f"Error: {str(e)}",
            ).model_dump(),
        ), 500


@bp.route("/docker/clear-all", methods=["POST"])
def debug_docker_stop_all():
    try:
        cleaned = docker.cleanup_containers()
        return jsonify({"containers_cleaned": cleaned})

    except Exception as e:
        return jsonify(
            ErrorResponse(
                status_code=500,
                message=f"Error: {str(e)}",
            ).model_dump(),
        ), 500
