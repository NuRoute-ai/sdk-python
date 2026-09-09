class NuRouteError(Exception):
    """Raised for every non-2xx response from the NuRoute gateway."""

    def __init__(
        self,
        status: int,
        message: str,
        error_type: str = "api_error",
        code: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.error_type = error_type
        self.code = code

    def __repr__(self) -> str:
        return (
            f"NuRouteError(status={self.status}, error_type={self.error_type!r}, "
            f"code={self.code!r}, message={str(self)!r})"
        )


# Deprecated alias — use NuRouteError instead. AICPError will be removed in a future major
# version.
#
# This is intentionally a plain assignment (`AICPError = NuRouteError`), not a subclass. The
# client only ever raises NuRouteError; if AICPError were `class AICPError(NuRouteError): ...`,
# existing user code written as `except AICPError:` would stop catching anything, since a
# subclass check only matches instances of the subclass or narrower, not its own base class.
# Aliasing keeps `except AICPError` and `isinstance(exc, AICPError)` working exactly as before.
AICPError = NuRouteError
