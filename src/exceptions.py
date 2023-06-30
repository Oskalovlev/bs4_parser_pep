class ParserFindTagException(Exception):
    """Вызывается, когда парсер не может найти тег."""
    pass


class NotFoundException(Exception):
    """Вызывается, когда парсер не может найти искомое."""
