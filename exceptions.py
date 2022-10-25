class IncorrectHTTPStatus(Exception):
    """Custom error for incorrect answer from Practicum API."""

    pass


class MissingTokens(Exception):
    """Custom error for missing env tokens."""

    pass
