"""
exceptions.py - Custom exception hierarchy for OzZoo.

All custom exceptions inherit from ZooException so callers can
catch the broad base or the specific type as needed.
"""


class ZooException(Exception):
    """Base class for all OzZoo-specific errors."""
    pass


class InsufficientFundsError(ZooException):
    """Raised when a purchase cannot be made due to low budget."""
    pass


class HabitatCapacityError(ZooException):
    """Raised when an enclosure has no space for an additional animal."""
    pass


class IncompatibleSpeciesError(ZooException):
    """Raised when a species is placed in an unsuitable habitat."""
    pass


class InsufficientFoodError(ZooException):
    """Raised when there is not enough food to feed an animal."""
    pass