import os
import random
from logging import getLogger

from locust import HttpUser, between, task

from utils import _cur_week_monday, _cur_week_monday_diff, _random_supplier_id, _random_supplier_ids  # type: ignore

logger = getLogger(__name__)


AUTH_TOKEN = os.getenv("AUTH_TOKEN")


class StressUser(HttpUser):
    wait_time = between(1, 3)
    auth_token = os.getenv("AUTH_TOKEN")
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}" if AUTH_TOKEN else None,
        "Content-Type": "application/json",
    }
    prefix = "/api/v1"
    tz = "Europe/Moscow"

    # example
    @classmethod
    def json(cls):
        return {"host": cls.host, "some_custom_arg": "example"}

    def on_start(self):
        user_id = id(self)
        logger.debug(f"User ID: '{user_id}' ({self.__class__.__name__}) started")

    @task(8)
    def index_post(self):
        payload = {
            "supplier_id": _random_supplier_id(),
            "start_dt": _cur_week_monday_diff(),
            "end_dt": _cur_week_monday(),
            "timezone": self.tz,
        }
        with self.client.post(
            self.prefix + "/index", json=payload, headers=self.headers, catch_response=True
        ) as response:
            if not response.ok:
                if response.status_code == 422:
                    logger.debug(f"HTTPError 422; payload={payload}, response.text={response.text}")
                response.failure(f"HTTPError {response.status_code}")

    @task(12)
    def index_batch_post(self):
        payload = {
            "supplier_ids": _random_supplier_ids(random.randint(2, 5)),
            "start_dt": _cur_week_monday_diff(),
            "end_dt": _cur_week_monday(),
            "timezone": self.tz,
        }
        with self.client.post(
            self.prefix + "/index-batch", json=payload, headers=self.headers, catch_response=True
        ) as response:
            if not response.ok:
                if response.status_code == 422:
                    logger.debug(f"HTTPError 422; payload={payload}, response.text={response.text}")
                response.failure(f"HTTPError {response.status_code}")

    @task(8)
    def index_history_post(self):
        payload = {
            "supplier_ids": _random_supplier_ids(random.randint(2, 5)),
            "start_dt": _cur_week_monday_diff(),
            "end_dt": _cur_week_monday(),
            "timezone": self.tz,
        }
        with self.client.post(
            self.prefix + "/index-history", json=payload, headers=self.headers, catch_response=True
        ) as response:
            if not response.ok:
                if response.status_code == 422:
                    logger.debug(f"HTTPError 422; payload={payload}, response.text={response.text}")
                response.failure(f"HTTPError {response.status_code}")

    @task(1)
    def index_history_archive_post(self):
        payload = {
            "supplier_ids": _random_supplier_ids(random.randint(2, 5)),
            "start_dt": _cur_week_monday_diff(),
            "end_dt": _cur_week_monday(),
            "timezone": self.tz,
        }
        with self.client.post(
            self.prefix + "/index-history-archive", json=payload, headers=self.headers, catch_response=True
        ) as response:
            if not response.ok:
                if response.status_code == 422:
                    logger.debug(f"HTTPError 422; payload={payload}, response.text={response.text}")
                response.failure(f"HTTPError {response.status_code}")

    @task(1)
    def index_detailed_report_post(self):
        payload = {
            "supplier_id": _random_supplier_id(),
            "create_dt": _cur_week_monday(),
            "timezone": self.tz,
        }
        with self.client.post(
            self.prefix + "/index-detailed-report", json=payload, headers=self.headers, catch_response=True
        ) as response:
            if not response.ok:
                if response.status_code == 422:
                    logger.debug(f"HTTPError 422; payload={payload}, response.text={response.text}")
                response.failure(f"HTTPError {response.status_code}")

    @task(12)
    def index_status_post(self):
        payload = {
            "end_dt": _cur_week_monday(),
            "timezone": self.tz,
        }
        with self.client.post(
            self.prefix + "/index-status", json=payload, headers=self.headers, catch_response=True
        ) as response:
            if not response.ok:
                if response.status_code == 422:
                    logger.debug(f"HTTPError 422; payload={payload}, response.text={response.text}")
                response.failure(f"HTTPError {response.status_code}")

    @task(8)
    def coefficient_list(self):
        with self.client.get(self.prefix + "/coefficient-list", headers=self.headers, catch_response=True) as response:
            if not response.ok:
                if response.status_code == 422:
                    logger.debug(f"HTTPError 422; payload=None, response.text={response.text}")
                response.failure(f"HTTPError {response.status_code}")

    def on_stop(self):
        user_id = id(self)
        logger.debug(f"User ID: '{user_id}' ({self.__class__.__name__}) stopped")
