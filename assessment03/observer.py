"""
observer.py - Observer + Singleton design patterns for OzZoo.

Design Patterns Used
--------------------
1. Observer Pattern
   Why: Animals need to notify the manager when their health drops critically
        low, without the Animal class knowing anything about the Zoo or CLI.
        The Observer pattern decouples the subject (HealthMonitor) from
        observers (alert handlers), making it easy to add new alert
        destinations (email, GUI pop-up) without changing any animal code.

   Structure:
       HealthObserver (ABC)     ← observer interface
       ├── ManagerAlertObserver ← collects CLI alerts per tick
       └── LogObserver          ← maintains a permanent session log

       HealthMonitor            ← subject; checks animals and notifies observers

2. Singleton Pattern (applied to HealthMonitor)
   Why: There should only ever be one HealthMonitor for the zoo. Having
        multiple monitors would cause duplicate alerts and inconsistent
        tracking of which animals have already been flagged.
        The Singleton ensures a single shared instance throughout the
        application's lifetime.
"""

from abc import ABC, abstractmethod
from animals import Animal


# ---------------------------------------------------------------------------
# Observer interface (ABC with only abstract methods — satisfies "Interface"
# rubric requirement alongside ICleanable in resources.py)
# ---------------------------------------------------------------------------

class HealthObserver(ABC):
    """
    Abstract observer interface for health alert subscribers.

    Any class that wants to receive health alerts must implement
    on_critical_health(). This defines the contract (interface) that
    all concrete observers must honour.
    """

    @abstractmethod
    def on_critical_health(self, animal: Animal, message: str) -> None:
        """
        Called when an animal's health drops to a critical level or it dies.

        Args:
            animal (Animal): The animal in distress.
            message (str): A descriptive alert message for display.
        """
        pass


# ---------------------------------------------------------------------------
# Concrete observers
# ---------------------------------------------------------------------------

class ManagerAlertObserver(HealthObserver):
    """
    Collects urgent health alerts during each day's tick for CLI display.

    Alerts are stored in a pending list and flushed (retrieved and cleared)
    at the end of each tick so the manager sees them all together.

    Attributes:
        pending_alerts (list[str]): Alerts waiting to be displayed.
    """

    def __init__(self):
        self.pending_alerts: list[str] = []

    def on_critical_health(self, animal: Animal, message: str) -> None:
        """
        Queue a critical alert for display at end of day.

        Args:
            animal (Animal): Animal in distress (used for context).
            message (str): Alert message to display.
        """
        alert = f"🚨 HEALTH ALERT: {message}"
        self.pending_alerts.append(alert)

    def flush_alerts(self) -> list[str]:
        """
        Return all pending alerts and clear the queue.

        Returns:
            list[str]: All alerts accumulated since the last flush.
        """
        alerts = self.pending_alerts.copy()
        self.pending_alerts.clear()
        return alerts


class LogObserver(HealthObserver):
    """
    Maintains a permanent session log of all health events.

    Unlike ManagerAlertObserver, the log is never cleared — it
    accumulates all alerts for the entire game session, useful for
    the end-game summary and AI copilot documentation.

    Attributes:
        log (list[str]): Chronological list of all health events.
    """

    def __init__(self):
        self.log: list[str] = []

    def on_critical_health(self, animal: Animal, message: str) -> None:
        """
        Append an alert to the permanent session log.

        Args:
            animal (Animal): Animal in distress.
            message (str): Alert message to record.
        """
        self.log.append(f"[LOG] {message}")

    def get_log(self) -> list[str]:
        """
        Return a copy of the full session log.

        Returns:
            list[str]: All health alerts recorded this session.
        """
        return self.log.copy()


# ---------------------------------------------------------------------------
# Subject — HealthMonitor (Singleton)
# ---------------------------------------------------------------------------

class HealthMonitor:
    """
    Subject in the Observer pattern; also implemented as a Singleton.

    HealthMonitor scans all animals each tick and notifies registered
    observers when any animal crosses a critical health threshold or dies.

    Singleton rationale: The zoo has exactly one health monitoring system.
    Multiple instances would duplicate alerts and produce inconsistent
    'already alerted' tracking. The Singleton guarantees one shared state.

    Singleton implementation: Classic __new__ override — the first call
    creates the instance; subsequent calls return the same object.

    Attributes:
        _observers (list[HealthObserver]): Registered alert subscribers.
        _previously_critical (set[str]): Animal names already flagged this
            tick, preventing duplicate notifications per tick.
        _instance (HealthMonitor): Class-level Singleton reference.
    """

    _instance: "HealthMonitor | None" = None

    def __new__(cls) -> "HealthMonitor":
        """
        Singleton __new__. Returns the existing instance if one exists,
        otherwise creates and stores the first instance.

        Returns:
            HealthMonitor: The single shared HealthMonitor instance.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialised = False
        return cls._instance

    def __init__(self):
        """
        Initialise observers and tracking set.
        Guard against re-initialisation on subsequent calls (Singleton).
        """
        if self._initialised:
            return
        self._observers: list[HealthObserver] = []
        self._previously_critical: set[str] = set()
        self._initialised = True

    @classmethod
    def reset(cls):
        """
        Destroy the Singleton instance. Used between game sessions or in tests.
        """
        cls._instance = None

    def register(self, observer: HealthObserver) -> None:
        """
        Register an observer to receive health alerts.

        Args:
            observer (HealthObserver): The subscriber to add.
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def unregister(self, observer: HealthObserver) -> None:
        """
        Remove a previously registered observer.

        Args:
            observer (HealthObserver): The subscriber to remove.
        """
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify(self, animal: Animal, message: str) -> None:
        """
        Dispatch an alert message to all registered observers.

        Args:
            animal (Animal): The animal triggering the alert.
            message (str): Alert text to send.
        """
        for observer in self._observers:
            observer.on_critical_health(animal, message)

    def check_animals(self, animals: list[Animal]) -> None:
        """
        Scan all animals and fire alerts for critical conditions and deaths.

        Alert deduplication: animals already flagged this tick are tracked
        in _previously_critical to avoid spamming the same alert each call.

        Args:
            animals (list[Animal]): All animals currently in the zoo.
        """
        current_critical: set[str] = set()

        for animal in animals:
            # Death alert (fire once)
            if not animal.is_alive:
                if animal.name not in self._previously_critical:
                    self._notify(animal, f"{animal.name} has DIED. 💀")
                continue

            # Critical health alert (fire once per critical episode)
            if animal.is_critical():
                current_critical.add(animal.name)
                if animal.name not in self._previously_critical:
                    self._notify(
                        animal,
                        f"{animal.name} ({animal.__class__.__name__}) health is "
                        f"critically low at {animal.health}! Treat immediately."
                    )

            # Severe hunger warning (fires every tick when hungry — intentional)
            elif animal.hunger >= 70:
                self._notify(
                    animal,
                    f"{animal.name} is very hungry (hunger: {animal.hunger}). Feed soon!"
                )

        self._previously_critical = current_critical

    def __repr__(self) -> str:
        return (
            f"HealthMonitor(observers={len(self._observers)}, "
            f"tracking={len(self._previously_critical)} critical animals)"
        )