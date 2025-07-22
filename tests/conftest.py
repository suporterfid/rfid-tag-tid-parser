import logging
import pytest

@pytest.fixture(scope="session", autouse=True)
def test_logger():
    handler = logging.FileHandler("test-log.txt", mode="w")
    formatter = logging.Formatter("%(asctime)s - %(message)s")
    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    yield
    logger.removeHandler(handler)
    handler.close()
