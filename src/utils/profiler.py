import time
from src.utils.logger import logger

def profile_function(func):
    """Decorator to measure and log the execution duration of a function."""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        logger.info(f"Performance: {func.__name__} took {duration:.6f}s")
        return result
    return wrapper
