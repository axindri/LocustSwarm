from datetime import datetime
from logging import getLogger

from models.tests import TestInfo


logger = getLogger(__name__)


def cleanup_old_stopped_tests(active_tests: list[TestInfo], max_age_seconds: int = 300):
    current_time = datetime.now()

    tests_to_remove = []

    for test in active_tests:
        if test.status in ["stopped", "completed", "err"]:
            try:
                start_time = datetime.fromisoformat(test.start_time)
                time_diff = (current_time - start_time).total_seconds()

                if time_diff > max_age_seconds:
                    tests_to_remove.append(test)
                    logger.info("Removing old test: %s (age: %d seconds)", test.test_id, time_diff)
            except (ValueError, KeyError) as e:
                logger.warning("Failed to parse start time for test %s: %s", test.test_id, e)
                tests_to_remove.append(test)

    for test in tests_to_remove:
        active_tests.remove(test)

    return len(tests_to_remove)
