from app.core.logging import get_logger, setup_logging


def test_logger_name_exists():
    setup_logging()
    logger = get_logger()
    assert logger.name == "app"
