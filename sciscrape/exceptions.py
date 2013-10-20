class ScrapeError(Exception): pass
class BadDOIError(ScrapeError): pass
class NotFoundError(Exception): pass
class NoAccessError(Exception): pass
class BadDocumentError(Exception): pass
