from datetime import datetime

from models.config import CustomScenario


def generate_custom_scenario_file(project: str, custom_scenario: CustomScenario) -> str:
    return f'''"""
Auto-generated LoadTestShape for {project}
Generated at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

from locust import LoadTestShape

class CustomLoadShape(LoadTestShape):
    config = {custom_scenario.model_dump_json(indent=4)}

    def tick(self):
        run_time = self.get_run_time()

        for stage in self.config.get('stages', []):
            if run_time < stage["duration"]:
                return (stage["users"], stage["spawn_rate"])
        return None
'''
