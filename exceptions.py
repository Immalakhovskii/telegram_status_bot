class IncorrectHTTPStatus(Exception):
    """Кастомная ошибка на некорретный статус ответа API Практикума."""

    pass


class MissingTokens(Exception):
    """Кастомная ошибка на отсутствие токенов."""

    pass
