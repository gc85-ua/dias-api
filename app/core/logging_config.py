import json
import logging
from datetime import UTC, datetime
from typing import Any, ClassVar

try:
    from opentelemetry import trace
except ImportError:
    trace = None


# Filter: Captures trace context immediately at log time (Thread & Queue safe)
class OtelContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:

        record.trace_id = None
        record.span_id = None
        record.trace_sampled = False

        if trace:
            span = trace.get_current_span()
            ctx = span.get_span_context()
            if ctx and ctx.is_valid:
                record.trace_id = format(ctx.trace_id, "032x")
                record.span_id = format(ctx.span_id, "016x")
                record.trace_sampled = bool(ctx.trace_flags.sampled)
        
        return True


# Formatter: Emits OTel-aligned JSON with ISO8601 UTC timestamps
class OtelJsonFormatter(logging.Formatter):
    RESERVED_ATTRS: ClassVar[set[str]] = {
        "args", "asctime", "created", "exc_info", "exc_text", "filename",
        "funcName", "levelname", "levelno", "lineno", "module", "msecs",
        "message", "msg", "name", "pathname", "process", "processName",
        "relativeCreated", "stack_info", "thread", "threadName", "taskName",
        "trace_id", "span_id", "trace_sampled"
    }

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "severity": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "trace_id": getattr(record, "trace_id", None),
            "span_id": getattr(record, "span_id", None),
            "trace_sampled": getattr(record, "trace_sampled", False),
        }

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        # Unpack standard extra kwargs dynamically: logger.info("...", extra={"user.id": 123})
        for key, val in record.__dict__.items():
            if key not in self.RESERVED_ATTRS and not key.startswith("_"):
                payload[key] = val

        return json.dumps(payload, default=str)
    
def configure_logging(level: int = logging.DEBUG) -> None:
    handler = logging.StreamHandler()
    handler.addFilter(OtelContextFilter())
    handler.setFormatter(OtelJsonFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers = [handler]

    for uvicorn_logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        uvicorn_logger = logging.getLogger(uvicorn_logger_name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.propagate = True