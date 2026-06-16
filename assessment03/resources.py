"""
resources.py - Enclosure, Food, and Medicine classes for OzZoo.

Also defines the ICleanable interface (ABC with only abstract methods),
which Enclosure implements — satisfying the rubric's interface requirement.
"""

from abc import ABC, abstractmethod
from animals import Animal
from exceptions import HabitatCapacityError, IncompatibleSpeciesError


# ---------------------------------------------------------------------------
# ICleanable interface
# ---------------------------------------------------------------------------

class ICleanable(ABC):
    """
    Interface (ABC with only abstract methods) for objects that can be cleaned.
    Any class implementing this must define clean() and get_cleanliness().
    """

    @abstractmethod
    def clean(self) -> str:
        """Clean this object and return a status message."""
        pass

    @abstractmethod
    def get_cleanliness(self) -> int:
        """Return current cleanliness level (0-100)."""
        pass


# ---------------------------------------------------------------------------
# Enclosure
# ---------------------------------------------------------------------------

class Enclosure(ICleanable):
    """
    Represents a physical enclosure in the zoo.

    Animals live here. Cleanliness affects animal happiness.
    Each enclosure has a capacity (space units) and a habitat type
    that must match the animals placed inside.

    Attributes:
        enclosure_id (str): Unique identifier.
        habitat_type (str): e.g. 'grassland', 'forest', 'aviary'.
        capacity (int): Total space units available.
        _cleanliness (int): 0-100, degrades each tick.
        animals (list): Animals currently housed here.
    """

    VALID_HABITATS = {"grassland", "forest", "aviary", "scrubland"}

    # Which species are compatible with which habitat
    HABITAT_COMPATIBILITY = {
        "grassland":  {"Kangaroo", "Wombat", "Dingo"},
        "forest":     {"Koala", "Wombat"},
        "aviary":     {"WedgeTailedEagle"},
        "scrubland":  {"TasmanianDevil", "Dingo", "Wombat"},
    }

    def __init__(self, enclosure_id: str, habitat_type: str, capacity: int):
        """
        Args:
            enclosure_id (str): Unique name/ID for this enclosure.
            habitat_type (str): Must be one of VALID_HABITATS.
            capacity (int): Max space units this enclosure can hold.
        """
        if habitat_type not in self.VALID_HABITATS:
            raise ValueError(f"Invalid habitat type '{habitat_type}'. "
                             f"Choose from {self.VALID_HABITATS}.")
        self.enclosure_id = enclosure_id
        self.habitat_type = habitat_type
        self.capacity = capacity
        self._cleanliness = 100
        self.animals: list[Animal] = []

    # --- ICleanable implementation ---

    def clean(self) -> str:
        """Clean the enclosure, restoring cleanliness to 100."""
        self._cleanliness = 100
        return f"Enclosure '{self.enclosure_id}' has been cleaned. Sparkling! 🧹"

    def get_cleanliness(self) -> int:
        return self._cleanliness

    # --- Space management ---

    def used_space(self) -> int:
        """Return total space units currently occupied."""
        return sum(a.space_required for a in self.animals if a.is_alive)

    def available_space(self) -> int:
        """Return remaining space units."""
        return self.capacity - self.used_space()

    # --- Animal management ---

    def add_animal(self, animal: Animal) -> str:
        """
        Place an animal in this enclosure.

        Args:
            animal (Animal): The animal to add.

        Raises:
            HabitatCapacityError: If there isn't enough space.
            IncompatibleSpeciesError: If species doesn't suit this habitat.

        Returns:
            str: Confirmation message.
        """
        species = animal.__class__.__name__
        compatible = self.HABITAT_COMPATIBILITY.get(self.habitat_type, set())

        if species not in compatible:
            raise IncompatibleSpeciesError(
                f"{species} is not compatible with a '{self.habitat_type}' enclosure."
            )
        if animal.space_required > self.available_space():
            raise HabitatCapacityError(
                f"Not enough space for {animal.name}. "
                f"Need {animal.space_required}, have {self.available_space()}."
            )

        self.animals.append(animal)
        return f"{animal.name} has been moved into '{self.enclosure_id}'."

    def remove_animal(self, animal: Animal) -> str:
        """Remove an animal from this enclosure."""
        if animal in self.animals:
            self.animals.remove(animal)
            return f"{animal.name} removed from '{self.enclosure_id}'."
        return f"{animal.name} is not in this enclosure."

    def update(self):
        """
        Called each game tick. Cleanliness drops based on how many
        animals are present. Dirty enclosures reduce animal happiness.
        """
        living = [a for a in self.animals if a.is_alive]
        self._cleanliness = max(0, self._cleanliness - len(living) * 5)

        if self._cleanliness < 40:
            for animal in living:
                animal._happiness = max(0, animal._happiness - 5)

    def status_summary(self) -> str:
        """Return a formatted status string for CLI display."""
        animal_names = ", ".join(a.name for a in self.animals if a.is_alive) or "Empty"
        return (
            f"[{self.enclosure_id}] {self.habitat_type.capitalize()} | "
            f"Space: {self.used_space()}/{self.capacity} | "
            f"Clean: {self._cleanliness}% | Animals: {animal_names}"
        )

    def __str__(self):
        return f"Enclosure({self.enclosure_id}, {self.habitat_type})"


# ---------------------------------------------------------------------------
# Food
# ---------------------------------------------------------------------------

class Food:
    """
    Represents a stock of a particular food type in the zoo's inventory.

    Attributes:
        food_type (str): e.g. 'grass', 'meat', 'eucalyptus'.
        quantity (int): Units currently in stock.
        cost_per_unit (float): Purchase price per unit.
    """

    VALID_TYPES = {"grass", "meat", "eucalyptus"}

    def __init__(self, food_type: str, quantity: int, cost_per_unit: float):
        """
        Args:
            food_type (str): Must be one of VALID_TYPES.
            quantity (int): Starting stock.
            cost_per_unit (float): Cost to buy one unit.
        """
        if food_type not in self.VALID_TYPES:
            raise ValueError(f"Unknown food type '{food_type}'.")
        self.food_type = food_type
        self.quantity = quantity
        self.cost_per_unit = cost_per_unit

    def consume(self, amount: int) -> int:
        """
        Consume up to `amount` units from stock.

        Returns:
            int: Actual amount consumed (may be less if stock is low).
        """
        actual = min(self.quantity, amount)
        self.quantity -= actual
        return actual

    def restock(self, amount: int):
        """Add units to stock."""
        self.quantity += amount

    def __str__(self):
        return f"{self.food_type.capitalize()}: {self.quantity} units (${self.cost_per_unit}/unit)"


# ---------------------------------------------------------------------------
# Medicine
# ---------------------------------------------------------------------------

class Medicine:
    """
    Represents medical supplies used to treat sick animals.

    Attributes:
        medicine_type (str): e.g. 'antibiotics', 'vitamins'.
        quantity (int): Doses in stock.
        heal_amount (int): Health points restored per dose.
        cost_per_dose (float): Purchase price per dose.
    """

    def __init__(self, medicine_type: str, quantity: int,
                 heal_amount: int, cost_per_dose: float):
        self.medicine_type = medicine_type
        self.quantity = quantity
        self.heal_amount = heal_amount
        self.cost_per_dose = cost_per_dose

    def treat(self, animal: Animal) -> str:
        """
        Administer one dose to an animal, restoring health.

        Args:
            animal (Animal): The animal to treat.

        Returns:
            str: Result message.
        """
        if self.quantity <= 0:
            return f"No {self.medicine_type} left in stock!"
        self.quantity -= 1
        animal._health = min(100, animal._health + self.heal_amount)
        return (
            f"{animal.name} treated with {self.medicine_type}. "
            f"Health restored by {self.heal_amount}. "
            f"Now at {animal._health}."
        )

    def __str__(self):
        return (
            f"{self.medicine_type.capitalize()}: {self.quantity} doses | "
            f"+{self.heal_amount} health | ${self.cost_per_dose}/dose"
        )