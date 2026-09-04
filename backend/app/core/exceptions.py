class ServiceError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ResourceNotFoundError(ServiceError):
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=404)


class ResourceConflictError(ServiceError):
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=409)


class RateLimitExceededError(ServiceError):
    def __init__(self, retry_after: int) -> None:
        super().__init__(
            (
                "LLM rate limit exceeded: maximum 10 calls per minute. "
                f"Retry in approximately {retry_after} seconds."
            ),
            status_code=429,
        )
        self.retry_after = retry_after


class DependencyUnavailableError(ServiceError):
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=503)
