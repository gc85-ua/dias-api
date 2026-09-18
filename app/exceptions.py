class AppError(Exception):
    def __init__(
        self,
        message: str,
        *,
        code: str = "INTERNAL_ERROR",
        category: str = "internal",
        retryable: bool = False,
        safe_message: str = "An unexpected error occurred",
        context: dict | None = None,
    ):
        super().__init__(message)
        self.code = code
        self.category = category
        self.retryable = retryable
        self.safe_message = safe_message
        self.context = context or {}

    def to_dict(self) -> dict:
        return {
            "error_code": self.code,
            "message": self.safe_message,
            "retryable": self.retryable,
        }


class ScrapingError(AppError):
    def __init__(self, message: str, *, url: str | None = None, context: dict | None = None, category: str = "dependency"):
        merged = {"url": url, **(context or {})} if url else (context or {})
        super().__init__(
            message,
            code="SCRAPING_FAILED",
            category=category,
            retryable=True,
            safe_message="Service temporarily unavailable. Please try again later.",
            context=merged,
        )


class ParsingError(AppError):
    def __init__(self, message: str, *, context: dict | None = None):
        super().__init__(
            message,
            code="PARSING_FAILED",
            category="data_integrity",
            retryable=False,
            safe_message="The data from the external source could not be processed.",
            context=context,
        )


class LocationNotFoundError(AppError):
    def __init__(self, location: str):
        super().__init__(
            f"No path found for location: {location}",
            code="LOCATION_NOT_FOUND",
            category="not_found",
            retryable=False,
            safe_message="The requested location was not found.",
            context={"location": location},
        )
