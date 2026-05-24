import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("files/logs.txt"),    # в файл
        logging.StreamHandler()            # и в stdout
    ]
)
logger = logging.getLogger("bot")
