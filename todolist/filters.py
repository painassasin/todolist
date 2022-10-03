import logging


class HealthCheckFilter(logging.Filter):

    def filter(self, record) -> bool:  # pragma: no cover
        return record.getMessage().find('/ping/') == -1
