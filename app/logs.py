import logging

RESET = "\x1b[0m"
BLACK = "\x1b[30m"
RED = "\x1b[31m"
GREEN = "\x1b[32m"
YELLOW = "\x1b[33m"
BLUE = "\x1b[34m"
MAGENTA = "\x1b[35m"
CYAN = "\x1b[36m"
WHITE = "\x1b[37m"


class ColoredFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": BLUE,
        "INFO": GREEN,
        "WARNING": YELLOW,
        "ERROR": RED,
        "CRITICAL": MAGENTA,
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, RESET)
        record.msg = f"{log_color}{record.msg}{RESET}"
        return super().format(record)


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)

if __name__ == "__main__":
    logger.debug("Это отладочное сообщение")
    logger.info("Это информационное сообщение")
    logger.warning("Это предупреждение")
    logger.error("Это сообщение об ошибке")
    logger.critical("Это критическое сообщение")
