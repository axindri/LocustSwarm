from logging import getLogger
from pathlib import Path

from flask import Blueprint, jsonify, send_file

from config.settings import settings
from models.errors import ErrorResponse
from utils.zip import make_zip

logger = getLogger(__name__)

bp = Blueprint("results", __name__, url_prefix="/api/results")


@bp.route("/<test_id>/report")
def get_test_report_html(test_id: str):
    try:
        project_scenario, timestamp = test_id.rsplit("-", 1)
        project, scenario = project_scenario.split("__", 1)

        results_dir = Path(settings.results_path) / project / scenario / test_id

        if not results_dir.exists():
            return jsonify(
                ErrorResponse(
                    status_code=404,
                    message="Results not found",
                ).model_dump(),
            ), 404

        report_path = results_dir / "report.html"

        if not report_path.exists():
            return jsonify(
                ErrorResponse(
                    status_code=404,
                    message="HTML report not found",
                ).model_dump(),
            ), 404

        with open(report_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        return html_content, 200, {"Content-Type": "text/html; charset=utf-8"}

    except Exception as e:
        logger.error("Failed to get test report: %s", e)
        return jsonify(
            ErrorResponse(
                status_code=500,
                message=f"Error: {str(e)}",
            ).model_dump(),
        ), 500


@bp.route("/<test_id>/download-zip")
def download_results_zip(test_id: str):
    try:
        project_scenario, timestamp = test_id.rsplit("-", 1)
        project, scenario = project_scenario.split("__", 1)

        results_dir = Path(settings.results_path) / project / scenario / test_id

        if not results_dir.exists():
            return jsonify({"error": "Results not found"}), 404

        files = list(results_dir.iterdir())
        if not files:
            return jsonify({"error": "No result files found"}), 404

        zip_buffer = make_zip(results_dir)

        return send_file(
            zip_buffer, as_attachment=True, download_name=f"{test_id}_results.zip", mimetype="application/zip"
        )

    except Exception as e:
        logger.error("Failed to create ZIP archive: %s", e)
        return jsonify(
            ErrorResponse(
                status_code=500,
                message=f"Error: {str(e)}",
            ).model_dump(),
        ), 500
