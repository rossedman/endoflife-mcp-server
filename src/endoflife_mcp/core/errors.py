"""Errors raised by the endoflife.date service.

Every failure the service anticipates is an :class:`EndOfLifeError`, so callers (the MCP
tools) can turn it into a message for the model without catching unrelated exceptions.
"""


class EndOfLifeError(Exception):
    """Base class for every error the service raises on purpose."""


class InvalidNameError(EndOfLifeError, ValueError):
    """A product, release, category or tag name cannot be a valid endoflife.date name."""


class NotFoundError(EndOfLifeError):
    """endoflife.date has no entry for the requested name."""


class RateLimitedError(EndOfLifeError):
    """endoflife.date asked the client to slow down (HTTP 429)."""

    def __init__(self, retry_after: str | None) -> None:
        """Build the error from the response's ``Retry-After`` header.

        Args:
            retry_after: The raw ``Retry-After`` header value, if the API sent one.
        """
        self.retry_after = retry_after
        hint = f" Retry after {retry_after} seconds." if retry_after else " Retry later."
        super().__init__("endoflife.date is rate limiting requests." + hint)


class UpstreamError(EndOfLifeError):
    """endoflife.date could not be reached, or answered with something unexpected."""
