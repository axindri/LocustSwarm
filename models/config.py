from pydantic import BaseModel


class Scenario(BaseModel):
    users: int = 1
    spawn_rate: int = 1
    run_time: str = "10s"


class Stage(BaseModel):
    duration: int = 10
    users: int = 20
    spawn_rate: int = 1


class CustomScenario(BaseModel):
    stages: list[Stage]


class ProjectConfigs(BaseModel):
    name: str
    host: str = "localhost"
    scenarios: dict[str, Scenario | CustomScenario]


class Config(BaseModel):
    projects_configs: dict[str, ProjectConfigs]
    # other prefs..
