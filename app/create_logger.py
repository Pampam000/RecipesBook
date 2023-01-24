import sys
from logging import getLogger, INFO, StreamHandler, Formatter, basicConfig

handler = StreamHandler(stream=sys.stdout)
handler.setFormatter(Formatter(
    fmt='%(asctime)s [%(levelname)s][%(filename)s: %(funcName)s: %(lineno)d]:'
        ' %(message)s'))

logger = getLogger(__name__)
logger.setLevel(INFO)
logger.addHandler(handler)
