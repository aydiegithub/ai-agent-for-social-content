from utils.logger import logger
from typing import Optional

class AydieException(Exception):
    def __init__(
        self,
        message: str,
        *,
        error_type: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Optional[dict] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_type = error_type or "AydieException"
        self.status_code = status_code or 500
        self.details = details or {}

        # Structured error logging
        logger.error(self.__str__())

    def __str__(self):
        base = f"[{self.error_type}] {self.message}"
        if self.details:
            return f"{base} | Details: {self.details}"
        return base

    def to_dict(self):
        """
        For API-style responses or structured logs.
        """
        return {
            "error": self.error_type,
            "message": self.message,
            "status_code": self.status_code,
            "details": self.details,
        }