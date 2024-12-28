class BokuException(Exception):
    """Base exception class for Boku errors"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class TaskfileError(BokuException):
    """Raised when there are issues with the taskfile"""

    pass


class TaskError(BokuException):
    """Raised when there are issues with task execution"""

    pass
