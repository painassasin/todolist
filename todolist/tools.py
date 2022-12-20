import functools
import logging
import time
from typing import Any, Callable

from django.db import connection, reset_queries

logger = logging.getLogger(__name__)


def query_debugger(func: Callable):  # pragma: no cover
    @functools.wraps(func)
    def inner_func(*args, **kwargs):
        reset_queries()

        start_queries: int = len(connection.queries)

        start: float = time.perf_counter()
        result: Any = func(*args, **kwargs)
        end: float = time.perf_counter()

        end_queries: int = len(connection.queries)

        logger.debug('Function : %s', func.__name__)
        logger.debug('Number of Queries : %d', end_queries - start_queries)
        logger.debug('Finished in %.2f', end - start)
        return result

    return inner_func
