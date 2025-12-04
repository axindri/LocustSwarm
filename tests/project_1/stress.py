from logging import getLogger

from locust import HttpUser, between


class StressUser(HttpUser):
    logger = getLogger("StressUser")
    wait_time = between(1, 5)

    def on_start(self):
        self.logger.info(f"User start {self.__class__.__name__} test")

    # Add some tests here

    def on_stop(self):
        self.logger.info(f"User stop {self.__class__.__name__} test")
