class DomainError(Exception):
    """Base exception for domain and application validation errors.

    Raise this (or a subclass) from use cases and domain services to
    signal business-rule violations.  The infrastructure API layer
    catches it and translates it into an HTTP 400 response.
    """
