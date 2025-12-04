import os
from datetime import datetime
from logging import getLogger
from pathlib import Path

import requests
from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from werkzeug.utils import secure_filename

from config.settings import settings
from db.db import database as db
from models.config import CustomScenario
from models.errors import ErrorResponse
from models.tests import StartTestRequest, StartTestResponse, StopTestResponse, TestInfo
from utils.cleaner import cleanup_old_stopped_tests
from utils.docker import docker
from utils.fakes import get_port_from_range
from utils.generator import generate_custom_scenario_file

logger = getLogger(__name__)

bp = Blueprint("tests", __name__, url_prefix="/api/tests")


@bp.route("/start", methods=["POST"])
def start_test():
    active_tests = db.get_tests()
    if len(active_tests) == 0:
        docker.cleanup_containers()
    if not settings.allow_parallel and docker.num_active_containers() > 0:
        test = active_tests[0]
        response = StartTestResponse(
            test_id=test.test_id,
            in_web=test.in_web,
            web_url=test.web_url,
            status="running",
            container_status=test.container_status,
        )
        return jsonify(response.model_dump())

    try:
        data = request.get_json()
        if not data:
            raise ValueError("No JSON data provided")

        start_request = StartTestRequest.model_validate(data)
    except ValidationError as e:
        logger.error("Validation error: %s", e)
        raise

    logger.debug("Got data: %s", start_request.model_dump())

    project = start_request.project
    scenario = start_request.scenario
    in_web = start_request.in_web
    auth_token = start_request.auth_token

    test_id_prefix = f"{project}__{scenario}"
    test_id = f"{test_id_prefix}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    logger.debug("test_id: %s", test_id)

    project_configs = settings.config.projects_configs[project]
    scenario_config = project_configs.scenarios[scenario]

    logger.debug("scenario_config: %s", scenario_config)

    for test in active_tests:
        if test.test_id.split("-")[0] == test_id_prefix and test.status != "completed":
            logger.debug("Test %s already running!", test)
            response = StartTestResponse(
                test_id=test.test_id,
                in_web=test.in_web,
                web_url=test.web_url,
                status="running",
                container_status=test.container_status,
            )
            return jsonify(response.model_dump())

    try:
        all_containers_before = docker.get().containers.list(all=True)
        logger.info("Containers before start: %s", [c.name for c in all_containers_before])
    except Exception as e:
        logger.error("Failed to list containers: %s", e)

    volumes = {
        os.path.abspath("./tests"): {"bind": "/tests", "mode": "ro"},
        os.path.abspath(settings.tmp_path): {"bind": "/tmp", "mode": "ro"},
    }

    environment = {
        "AUTH_TOKEN": auth_token,
        "PYTHONPATH": "/tests/",
    }
    results_volume = docker.setup_results_volume(project, scenario, test_id)
    volumes.update(results_volume)

    results_path = f"/results/{project}/{scenario}/{test_id}"

    if isinstance(scenario_config, CustomScenario):
        custom_scenario_content = generate_custom_scenario_file(project, scenario_config)
        logger.debug(custom_scenario_content)

        tmp_dir = Path(settings.tmp_path) / secure_filename(project)
        tmp_dir.mkdir(parents=True, exist_ok=True)

        custom_scenario_path = tmp_dir / "custom_scenario.py"
        with open(custom_scenario_path, "w", encoding="utf-8") as f:
            f.write(custom_scenario_content)

    command = f"""
        -f /tests/{project}/{scenario}.py{f",/tmp/{project}/custom_scenario.py" if isinstance(scenario_config, CustomScenario) else ""}
        {"--loglevel DEBUG" if settings.debug else ""}
        --host {project_configs.host}
        --web-port 8089
        --html {results_path}/report.html
        --csv {results_path}/stats
        --csv-full-history
        {"--headless" if not in_web else ""}
    """

    if not isinstance(scenario_config, CustomScenario):
        command += f"""
            --users {scenario_config.users}
            --spawn-rate {scenario_config.spawn_rate} 
            --run-time {scenario_config.run_time}
        """

    command = command.strip().replace("\n", " ")

    container = docker.get().containers.run(
        "locustio/locust:latest",
        command=command,
        volumes=volumes,
        ports={"8089/tcp": 8080 if not settings.allow_parallel else get_port_from_range()},
        detach=True,
        name=f"locust_{test_id}",
        environment=environment,
    )

    container.reload()
    if container.status != "running":
        logs = container.logs().decode("utf-8")[:500]
        logger.error("Container failed to start. Status: %s, Logs: %s", container.status, logs)
        container.stop()
        raise ValueError(f"Container failed to start. Status: {container.status}")

    locust_web_port = container.ports["8089/tcp"][0]["HostPort"]
    container_id = container.id or "unknown"
    container_status = container.status or "unknown"

    active_tests.append(
        TestInfo(
            test_id=test_id,
            status="running",
            project=project_configs.name,
            scenario=scenario,
            in_web=in_web,
            web_url=f"{settings.host}:{locust_web_port}",
            container_id=container_id,
            container_status=container_status,
            start_time=datetime.now().isoformat(),
        )
    )

    return jsonify(
        StartTestResponse(
            test_id=test_id,
            in_web=in_web,
            web_url=f"{settings.host}:{locust_web_port}",
            status="started",
            container_status=container_status,
        ).model_dump()
    )


@bp.route("/stop/<test_id>", methods=["POST"])
def stop_test(test_id: str):
    active_tests = db.get_tests()
    for test in active_tests:
        if test.test_id == test_id:
            try:
                container = docker.get().containers.get(test.container_id)

                if test.in_web:
                    report_url = f"{test.web_url}/stats/report"
                    response = requests.get(report_url, timeout=10)

                    if response.status_code == 200:
                        project, scenario = test.test_id.split("-")[0].split("__", 1)
                        results_dir = Path(settings.results_path) / project / scenario / test_id
                        results_dir.mkdir(parents=True, exist_ok=True)

                        report_path = results_dir / "report.html"
                        with open(report_path, "w", encoding="utf-8") as f:
                            f.write(response.text)

                        logger.info("HTML report saved: %s", report_path)
                    else:
                        logger.warning("Failed to download report: %s", response.status_code)

                container.stop(timeout=10)
                container.reload()
                container_status = container.status or "unknown"
                return jsonify(
                    StopTestResponse(
                        test_id=test.test_id,
                        status="stopped",
                        container_status=container_status,
                        message="Success",
                    ).model_dump()
                )
            except Exception as e:
                return jsonify(
                    StopTestResponse(
                        test_id=test.test_id,
                        status="err",
                        container_status="err",
                        message=f"Failed: {str(e)}",
                    ).model_dump()
                )
    return jsonify(
        StopTestResponse(
            test_id="err",
            status="err",
            container_status="err",
            message="Failed",
        ).model_dump()
    )


@bp.route("/clear-all", methods=["POST"])
def stop_all_tests():
    active_tests = db.get_tests()
    try:
        cleaned = docker.cleanup_containers()
        active_tests_qty = len(active_tests)
        active_tests.clear()
        return jsonify({"active_tests_cleaned": active_tests_qty, "containers_cleaned": cleaned})

    except Exception as e:
        return jsonify(
            ErrorResponse(
                status_code=500,
                message=f"Error: {str(e)}",
            ).model_dump(),
        ), 500


@bp.route("/active")
def get_active_tests():
    active_tests = db.get_tests()

    removed_count = cleanup_old_stopped_tests(active_tests, settings.active_tests_cleanup_timeout)
    if removed_count > 0:
        logger.info("Cleaned up %d old tests", removed_count)

    # logger.debug("Active tests: %s", active_tests)
    response = []
    for test in active_tests:
        try:
            container = docker.get().containers.get(test.container_id)
            test.container_status = container.status or "unknown"
            if container.status != "running":
                test.status = "completed"
        except Exception as e:
            logger.debug("Failed get active_tests: %s", str(e))
            test.status = "completed"
        response.append(test.model_dump())
    response.reverse()
    return jsonify(response)


@bp.route("/completed")
def get_completed_tests():
    try:
        results_path = Path(settings.results_path)

        if not results_path.exists():
            return jsonify([])

        completed_tests = []

        for project_dir in results_path.iterdir():
            if not project_dir.is_dir():
                continue

            for scenario_dir in project_dir.iterdir():
                if not scenario_dir.is_dir():
                    continue

                for test_dir in scenario_dir.iterdir():
                    if not test_dir.is_dir():
                        continue

                    completed_tests.append(test_dir.name)

        def extract_timestamp(name):
            if "-" in name:
                timestamp_part = name.split("-")[-1]
                if timestamp_part.isdigit() and len(timestamp_part) >= 14:
                    return int(timestamp_part[:14])
            return 0

        completed_tests.sort(key=extract_timestamp, reverse=True)

        return jsonify(completed_tests)

    except Exception as e:
        logger.error("Failed to get completed tests: %s", e)
        return jsonify(
            ErrorResponse(
                status_code=500,
                message=f"Error: {str(e)}",
            ).model_dump(),
        ), 500
