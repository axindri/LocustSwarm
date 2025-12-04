from logging import getLogger

from locust import HttpUser, between, task

logger = getLogger("MetricsUser")


class MetricsUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        logger.debug(f"User start {self.__class__.__name__} test")

    @task(1)
    def liveness(self):
        self.client.get("/liveness")

    @task(1)
    def readiness(self):
        self.client.get("/readiness")

    @task(1)
    def info(self):
        self.client.get("/")

    @task(1)
    def metrics(self):
        self.client.get("/metrics")

    def on_stop(self):
        logger.debug(f"User stop {self.__class__.__name__} test")
