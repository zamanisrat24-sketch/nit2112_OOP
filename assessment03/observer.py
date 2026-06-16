"""
observer.py - Observer design pattern for OzZoo health alert system.

Design Pattern: Observer
Why: Animals need to notify the manager when their health drops critically low,
     without the Animal class needing to know anything about the Zoo or CLI.
     The Observer pattern decouples the subject (Animal stats) from the
     observers (alert handlers like CLI printer or logger).

Structure:
    HealthObserver (ABC)  ← observer interface
    ├── ManagerAlertObserver  ← prints alerts to CLI
    └── LogObserver           ← records alerts to a log list

    HealthMonitor  ← subject; checks animals and notifies observers
"""

from abc import ABC, abstractmethod
from animals import Animal


# ---------------------------------------------------------------------------
# Observer interface
# ---------------------------------------------------------------------------

class HealthObserver(ABC):
    """
    Abstract observer. Any class that wants health alerts must implement
    on_critical_health().
    """

    @abstractmethod
    def on_critical_health(self, animal: Animal, message: str):
        """
        Called when an animal's health drops to a critical level.

        Args:
            animal (Animal): The animal in distress.
            message (str): A descriptive alert message.
        """
        pass


# ---------------------------------------------------------------------------
# Concrete observers
# ---------------------------------------------------------------------------

class ManagerAlertObserver(HealthObserver):
    """
    Prints urgent health alerts directly to the CLI.
    Collects alerts for the current tick to display at end of day.
    """

    def __init__(self):
        self.pending_alerts: list[str] = []

    def on_critical_health(self, animal: Animal, message: str):
        alert = f"🚨 HEALTH ALERT: {message}"
        self.pending_alerts.append(alert)

    def flush_alerts(self) -> list[str]:
        """Return and clear all pending alerts."""
        alerts = self.pending_alerts.copy()
        self.pending_alerts.clear()
        return alerts


class LogObserver(HealthObserver):
    """
    Records all health alerts to an internal log.
    Useful for the documentation / AI copilot log.
    """

    def __init__(self):
        self.log: list[str] = []

    def on_critical_health(self, animal: Animal, message: str):
        self.log.append(f"Day alert — {message}")

    def get_log(self) -> list[str]:
        return self.log.copy()


# ---------------------------------------------------------------------------
# Subject (Health Monitor)
# ---------------------------------------------------------------------------

class HealthMonitor:
    """
    Subject in the Observer pattern.

    Checks all animals each tick and notifies registered observers
    when any animal's health crosses critical thresholds.

    Attributes:
        _observers (list[HealthObserver]): Registered observers.
        _previously_critical (set): Tracks animals already alerted this tick
            to avoid duplicate notifications.
    """

    def __init__(self):
        self._observers: list[HealthObserver] = []
        self._previously_critical: set = set()

    def register(self, observer: HealthObserver):
        """
        Register an observer to receive health alerts.

        Args:
            observer (HealthObserver): Observer to add.
        """
        self._observers.append(observer)

    def unregister(self, observer: HealthObserver):
        """Remove an observer."""
        self._observers.remove(observer)

    def _notify(self, animal: Animal, message: str):
        """Notify all registered observers of an alert."""
        for observer in self._observers:
            observer.on_critical_health(animal, message)

    def check_animals(self, animals: list[Animal]):
        """
        Scan all animals and fire alerts for critical or deceased animals.

        Args:
            animals (list[Animal]): All living animals to check.
        """
        current_critical = set()

        for animal in animals:
            if not animal.is_alive:
                if animal.name not in self._previously_critical:
                    self._notify(animal, f"{animal.name} has DIED.")
                continue

            if animal.is_critical():
                current_critical.add(animal.name)
                if animal.name not in self._previously_critical:
                    self._notify(
                        animal,
                        f"{animal.name} ({animal.__class__.__name__}) health is "
                        f"critically low at {animal.health}! Treat immediately."
                    )

            elif animal.hunger >= 70:
                self._notify(
                    animal,
                    f"{animal.name} is very hungry (hunger: {animal.hunger}). Feed soon!"
                )

        self._previously_critical = current_critical