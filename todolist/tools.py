import functools
import logging
import time

from django.db import connection, reset_queries

logger = logging.getLogger(__name__)


def query_debugger(func):
    @functools.wraps(func)
    def inner_func(*args, **kwargs):
        reset_queries()

        start_queries = len(connection.queries)

        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()

        end_queries = len(connection.queries)

        logger.debug('Function : %s', func.__name__)
        logger.debug('Number of Queries : %d', end_queries - start_queries)
        logger.debug('Finished in %.2f', end - start)
        return result

    return inner_func
