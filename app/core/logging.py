"""Standard-library logging facade; structured logging is optional at deployment."""
import logging
def get_logger(name=None): return logging.getLogger(name or 'simorgh')
