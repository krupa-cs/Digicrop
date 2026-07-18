import logging
import os

def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger with standard formatting.
    """
    logger = logging.getLogger(name)
    
    # Check if we are running in Lambda (AWS sets some env vars)
    # Only configure formatting if not already configured by Lambda environment
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))
    return logger
