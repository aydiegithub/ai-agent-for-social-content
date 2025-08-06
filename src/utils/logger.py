import logging
import os

class AydieLogger:
    def __init__(self, name: str = "aydie-logger", log_dir: str = "logs", log_file: str = "project.log"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # Ensure log directory exists
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, log_file)

        # Formatter
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")

        # File handler
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        # Add handlers if not already added
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger

# Create a shared logger instance
logging = AydieLogger().get_logger()