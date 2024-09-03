import logging

logger = logging.getLogger("Bit")
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s|%(levelname)s|%(name)s|%(message)s"))
