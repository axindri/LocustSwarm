from dataclasses import dataclass, field
from typing import Any

from models.tests import TestInfo


@dataclass
class Database:
    _tests: list[TestInfo] = field(default_factory=list)

    def get(self, attr: str) -> Any:
        if hasattr(self, attr):
            return getattr(self, attr)
        raise AttributeError(f"Attribute '{attr}' not found")

    def set(self, attr: str, value: Any) -> bool:
        if hasattr(self, attr):
            setattr(self, attr, value)
            return True
        return False

    def get_tests(self):
        return self._tests

    def add_test(self, test: TestInfo) -> tuple[bool, list[TestInfo]]:
        self._tests.append(test)
        return True, self._tests

    def remove_test(self, test_id: str) -> tuple[bool, list[TestInfo]]:
        for i, test in enumerate(self._tests):
            if test.test_id == test_id:
                self._tests.pop(i)
                return True, self._tests
        return False, self._tests

    def remove_all_tests(self) -> bool:
        self._tests.clear()
        return True


database = Database()
