import logging
import os
import json
from datetime import datetime
import re

class SensitiveDataFilter(logging.Filter):
    """
    Filter to mask sensitive data in logs
    """
    def __init__(self, patterns=None):
        super().__init__()
        self.patterns = patterns or [
            (re.compile(r'(password["\']\s*:\s*["\'])(.+?)(["\'])'), r'\1********\3'),
            (re.compile(r'(Authorization["\']\s*:\s*["\']Bearer\s+)(.+?)(["\'])'), r'\1********\3'),
            (re.compile(r'(api_key["\']\s*:\s*["\'])(.+?)(["\'])'), r'\1********\3'),
            (re.compile(r'(access_token["\']\s*:\s*["\'])(.+?)(["\'])'), r'\1********\3'),
            (re.compile(r'(refresh_token["\']\s*:\s*["\'])(.+?)(["\'])'), r'\1********\3'),
        ]
    
    def filter(self, record):
        if isinstance(record.msg, str):
            for pattern, replacement in self.patterns:
                record.msg = pattern.sub(replacement, record.msg)
        return True

class JSONFormatter(logging.Formatter):
    """
    Format logs as JSON for easier parsing by log management systems
    """
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process": record.process,
            "thread": record.thread,
        }
        
        # Add exception info if available
        if record.exc_info:
            log_record["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
        
        # Add extra attributes
        for key, value in record.__dict__.items():
            if key not in [
                "args", "asctime", "created", "exc_info", "exc_text", "filename",
                "funcName", "id", "levelname", "levelno", "lineno", "module",
                "msecs", "message", "msg", "name", "pathname", "process",
                "processName", "relativeCreated", "stack_info", "thread", "threadName"
            ]:
                log_record[key] = value
        
        return json.dumps(log_record)

def setup_logging():
    """
    Configure logging with security in mind
    """
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Create handlers
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler("logs/app.log")
    security_handler = logging.FileHandler("logs/security.log")
    
    # Set log levels
    console_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.DEBUG)
    security_handler.setLevel(logging.WARNING)
    
    # Create formatters
    standard_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s'
    )
    json_formatter = JSONFormatter()
    
    # Add formatters to handlers
    console_handler.setFormatter(standard_formatter)
    file_handler.setFormatter(json_formatter)
    security_handler.setFormatter(json_formatter)
    
    # Add sensitive data filter to all handlers
    sensitive_filter = SensitiveDataFilter()
    console_handler.addFilter(sensitive_filter)
    file_handler.addFilter(sensitive_filter)
    security_handler.addFilter(sensitive_filter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Configure security logger
    security_logger = logging.getLogger("security")
    security_logger.setLevel(logging.WARNING)
    security_logger.addHandler(security_handler)
    
    # Configure FastAPI logger
    fastapi_logger = logging.getLogger("fastapi")
    fastapi_logger.setLevel(logging.INFO)
    
    # Configure uvicorn access logger
    uvicorn_logger = logging.getLogger("uvicorn.access")
    uvicorn_logger.setLevel(logging.INFO)
    
    return root_logger

# Initialize logging
logger = setup_logging()