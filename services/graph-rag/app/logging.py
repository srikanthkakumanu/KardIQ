import logging
import sys
from contextvars import ContextVar

# Set by RequestIdMiddleware per request; read here so every log line can
# include the correlation id without threading it through every call site.
request_id_var: ContextVar[str] = ContextVar("request_id", default="none")


class RequestIdLogFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


def configure_logging(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(RequestIdLogFilter())
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)-8s [requestId=%(request_id)s] %(name)s - %(message)s"
        )
    )

    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level)
