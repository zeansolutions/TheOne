import os
import logging

# Ensure logs directory exists
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logger = logging.getLogger("TheOne")
logger.setLevel(logging.INFO)

# File handler
file_handler = logging.FileHandler(os.path.join(log_dir, "theone.log"), encoding="utf-8")
file_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
