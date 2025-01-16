class BokuException(Exception):
    """Base exception class for Boku errors"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class BokuTaskfileError(BokuException):
    """Raised when there are issues with the taskfile"""

    pass


class BokuTaskError(BokuException):
    """Raised when there are issues with task execution"""

    pass


class BokuDependencyError(BokuException):
    """Task dependency errors"""

    pass


class BokuVariableError(BokuException):
    """Variable resolution errors"""

    pass


class BokuHelperError(BokuException):
    """Helper errors"""

    pass
