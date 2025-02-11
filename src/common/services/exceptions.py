from src.core.exceptions import ApplicationException


class ServiceException(ApplicationException):
    def __init__(self, message: str) -> None:
        self.message: str = message

    def __str__(self) -> str:
        return self.message


class NotificationServiceException(ApplicationException):
    def __init__(self, message: str) -> None:
        self.message: str = message

    def __str__(self) -> str:
        return self.message
