import os
import logging
import sys

os.makedirs("logs", exist_ok=True)
logger = logging.getLogger("Мужики, хотите фокус? ")

logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

file_handler = logging.FileHandler("logs/app.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
