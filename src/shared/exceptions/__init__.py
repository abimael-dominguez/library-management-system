# Custom exceptions for the LMS application

class LMSException(Exception):
    """Base exception for LMS application"""
    pass

class BookNotFoundError(LMSException):
    """Raised when a book is not found"""
    pass

class MemberNotFoundError(LMSException):
    """Raised when a member is not found"""
    pass

class LoanNotFoundError(LMSException):
    """Raised when a loan is not found"""
    pass

class ValidationError(LMSException):
    """Raised when validation fails"""
    pass
