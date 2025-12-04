from pydantic import BaseModel


class StartTestRequest(BaseModel):
    project: str
    scenario: str
    auth_token: str
    in_web: bool
    


class TestInfo(BaseModel):
    test_id: str
    status: str
    project: str
    scenario: str
    in_web: bool
    web_url: str
    container_id: str
    container_status: str
    start_time: str


class StartTestResponse(BaseModel):
    test_id: str
    in_web: bool
    web_url: str
    status: str
    container_status: str


class StopTestResponse(BaseModel):
    test_id: str
    status: str
    container_status: str
    message: str
