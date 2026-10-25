import json
import logging
import os
import sys
from datetime import UTC, datetime, timezone


class JsonFormatter(logging.Formatter):
    def format(self, record):
        item = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            item["exception"] = self.formatException(record.exc_info)
        return json.dumps(item)


def configure_logging(app):
    level = os.getenv("LOG_LEVEL", app.config.get("LOG_LEVEL", "INFO"))
    output_format = os.getenv(
        "LOG_FORMAT", app.config.get("LOG_FORMAT", "text")
    ).lower()

    handler = logging.StreamHandler(sys.stdout)
    if output_format == "json":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s: %(message)s"
        ))

    app.logger.handlers.clear()
    app.logger.addHandler(handler)
    app.logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    app.logger.propagate = False
    return app.logger
