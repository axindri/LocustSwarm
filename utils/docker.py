import os
from dataclasses import dataclass
from logging import getLogger
from pathlib import Path

from docker import DockerClient
from docker.models.containers import Container

from config.settings import settings

logger = getLogger(__name__)


@dataclass
class Docker:
    client: DockerClient

    def get(self) -> DockerClient:
        return self.client

    def cleanup_containers(self) -> int:
        try:
            logger.info("Starting Docker cleanup...")

            running_containers: list[Container] = self.client.containers.list(filters={"status": "running"})
            if running_containers:
                logger.info("Stopping %s running containers...", len(running_containers))
                for container in running_containers:
                    try:
                        container.stop()
                        logger.debug("Stopped container: %s", container.name)
                    except Exception as e:
                        logger.warning("Failed to stop container %s: %s", container.name, e)

            all_containers: list[Container] = self.client.containers.list(all=True)
            if all_containers:
                logger.info("Removing %s containers...", len(all_containers))
                for container in all_containers:
                    try:
                        container.remove(force=True)
                        logger.debug("Removed container: %s", container.name)
                    except Exception as e:
                        logger.warning("Failed to remove container %s: %s", container.name, e)
            return len(all_containers)
        except Exception as e:
            logger.error("Docker cleanup failed: %s", e)
            return 0
        
    def num_active_containers(self):
        running_containers: list[Container] = self.client.containers.list(filters={"status": "running"})
        return len(running_containers)

    def setup_results_volume(self, project: str, scenario: str, test_id: str) -> dict[str, dict[str, str]]:
        results_dir = Path(settings.results_path) / project / scenario / test_id
        results_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(results_dir, 0o777)
        container_results_dir = f"/results/{project}/{scenario}/{test_id}"

        return {str(results_dir.absolute()): {"bind": container_results_dir, "mode": "rw"}}


docker = Docker(client=DockerClient(base_url=settings.docker_base_url))
