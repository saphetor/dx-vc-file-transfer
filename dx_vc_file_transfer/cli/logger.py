import logging


def _get_logger():
    """
    Returns a logger instance for the dx_vc_file_transfer module.
    """
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger("dx_vc_file_transfer")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


logger = _get_logger()
