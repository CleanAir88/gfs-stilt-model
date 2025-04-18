class StiltException(Exception):
    """A STILT error occurred."""


class JobException(StiltException):
    """A job error occurred."""


class MetNotFoundException(StiltException):
    """Input meteorological data files are missing."""
