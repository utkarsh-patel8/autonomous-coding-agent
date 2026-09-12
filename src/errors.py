class ProviderInfrastructureError(Exception):
    """
    Raised when an LLM request fails because of provider/network
    infrastructure rather than an agent/repository error.
    """

    def __init__(
        self,
        message: str,
        provider: str = "groq",
        failure_type: str = "unknown",
        status_code: int | None = None,
    ):
        super().__init__(message)

        self.provider = provider
        self.failure_type = failure_type
        self.status_code = status_code

    def to_dict(self) -> dict:
        return {
            "provider": self.provider,
            "failure_type": self.failure_type,
            "status_code": self.status_code,
            "message": str(self),
        }