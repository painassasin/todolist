import logging
import time

from django.core.handlers.wsgi import WSGIRequest
from django.db import connection, reset_queries


class QueryDebuggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger(__name__)

    def __call__(self, request: WSGIRequest):
        reset_queries()

        start_queries = len(connection.queries)

        start = time.perf_counter()

        response = self.get_response(request)

        end = time.perf_counter()

        end_queries = len(connection.queries)
        queries = end_queries - start_queries
        if queries:
            self.logger.debug(request)

            for query in connection.queries:
                self.logger.debug(query)
            self.logger.debug('Number of Queries: %d', queries)
            self.logger.debug('Estimated %.2f ms', (end - start) * 1000)

        return response
