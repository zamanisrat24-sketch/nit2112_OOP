"""
animals.py - Animal class hierarchy for OzZoo simulation.

Hierarchy:
    Animal (ABC)
    ├── Mammal
    │   ├── Marsupial → Kangaroo, Koala, Wombat
    │   └── Carnivore → TasmanianDevil, Dingo
    └── Bird
        └── RaptorBird → WedgeTailedEagle
"""

from abc import ABC, abstractmethod
import random


# ---------------------------------------------------------------------------
# Abstract Base Class
# ---------------------------------------------------------------------------

class Animal(ABC):
    """
    Abstract base class for all animals in OzZoo.

    Every animal has core welfare stats (health, hunger, happiness) and
    must implement make_sound(), eat(), and get_info().

    Attributes:
        name (str): The animal's individual name.
        age (int): Age in years.
        _health (int): Health points 0-100 (protected).
        _hunger (int): Hunger level 0-100; higher = more hungry (protected).
        _happiness (int): Happiness 0-100 (protected).
        is_alive (bool): Whether the animal is alive.
        food_type (str): The type of food this animal eats.
        space_required (int): Enclosure space units needed.
    """

    def __init__(self, name: str, age: int, food_type: str, space_required: int):
        self.name = name
        self.age = age
        self._health = 100
        self._hunger = 0       # 0 = full, 100 = starving
        self._happiness = 80
        self.is_alive = True
        self.food_type = food_type
        self.space_required = space_required

    # --- Abstract methods every subclass MUST implement ---

    @abstractmethod
    def make_sound(self) -> str:
        """Return the sound this animal makes."""
        pass

    @abstractmethod
    def eat(self, food_amount: int) -> str:
        """
        Feed the animal and reduce hunger.

        Args:
            food_amount (int): Units of food provided.

        Returns:
            str: A description of the animal eating.
        """
        pass

    @abstractmethod
    def get_info(self) -> str:
        """Return a species-specific description of this animal."""
        pass

    # --- Concrete shared methods ---

    @property
    def health(self) -> int:
        return self._health

    @property
    def hunger(self) -> int:
        return self._hunger

    @property
    def happiness(self) -> int:
        return self._happiness

    def update_stats(self):
        """
        Called each game tick. Increases hunger, adjusts health and happiness.
        Animals deteriorate if hungry or unhealthy.
        """
        if not self.is_alive:
            return

        # Hunger rises each tick
        self._hunger = min(100, self._hunger + 10)

        # Starving animals lose health and happiness
        if self._hunger >= 80:
            self._health = max(0, self._health - 15)
            self._happiness = max(0, self._happiness - 10)
        elif self._hunger >= 50:
            self._happiness = max(0, self._happiness - 5)

        # Death check
        if self._health <= 0:
            self.is_alive = False

    def is_critical(self) -> bool:
        """Return True if this animal's health is critically low (≤ 30)."""
        return self._health <= 30

    def can_breed(self) -> bool:
        """Return True if this animal is healthy and happy enough to breed."""
        return self._health >= 70 and self._happiness >= 70 and self.is_alive

    def status_summary(self) -> str:
        """Return a one-line welfare summary for display in the CLI."""
        status = "💀 DEAD" if not self.is_alive else (
            "🔴 CRITICAL" if self.is_critical() else
            "🟡 POOR" if self._health < 60 else "🟢 OK"
        )
        return (
            f"{self.name} ({self.__class__.__name__}) | "
            f"Health: {self._health} | Hunger: {self._hunger} | "
            f"Happiness: {self._happiness} | {status}"
        )

    def __str__(self):
        return f"{self.name} the {self.__class__.__name__}"


# ---------------------------------------------------------------------------
# Mammal branch
# ---------------------------------------------------------------------------

class Mammal(Animal):
    """
    Intermediate class for all mammals.
    Adds fur_colour and a shared groom() behaviour.
    """

    def __init__(self, name: str, age: int, food_type: str,
                 space_required: int, fur_colour: str):
        super().__init__(name, age, food_type, space_required)
        self.fur_colour = fur_colour

    def groom(self) -> str:
        """Grooming boosts happiness slightly."""
        self._happiness = min(100, self._happiness + 5)
        return f"{self.name} is grooming itself. Happiness +5."


class Marsupial(Mammal):
    """
    Marsupials — native Australian pouched mammals.
    Adds a pouch_young attribute for breeding flavour.
    """

    def __init__(self, name: str, age: int, food_type: str,
                 space_required: int, fur_colour: str):
        super().__init__(name, age, food_type, space_required, fur_colour)
        self.pouch_young = 0   # number of joeys currently in pouch

    def get_info(self) -> str:
        return (
            f"{self.name} is a marsupial with {self.fur_colour} fur. "
            f"Joeys in pouch: {self.pouch_young}."
        )


class Carnivore(Mammal):
    """
    Carnivorous mammals. Has a prey_drive stat that affects happiness
    if not fed meat regularly.
    """

    def __init__(self, name: str, age: int, space_required: int, fur_colour: str):
        super().__init__(name, age, "meat", space_required, fur_colour)
        self.prey_drive = random.randint(60, 90)

    def get_info(self) -> str:
        return (
            f"{self.name} is a carnivore with {self.fur_colour} fur. "
            f"Prey drive: {self.prey_drive}."
        )


# ---------------------------------------------------------------------------
# Bird branch
# ---------------------------------------------------------------------------

class Bird(Animal):
    """
    Intermediate class for all birds.
    Adds wingspan and a perch() behaviour.
    """

    def __init__(self, name: str, age: int, food_type: str,
                 space_required: int, wingspan_cm: int):
        super().__init__(name, age, food_type, space_required)
        self.wingspan_cm = wingspan_cm

    def perch(self) -> str:
        """Birds perch to rest; small happiness boost."""
        self._happiness = min(100, self._happiness + 3)
        return f"{self.name} spreads its {self.wingspan_cm}cm wings and perches. Happiness +3."

    def get_info(self) -> str:
        return f"{self.name} is a bird with a {self.wingspan_cm}cm wingspan."


class RaptorBird(Bird):
    """
    Birds of prey. Has a hunt_skill stat.
    """

    def __init__(self, name: str, age: int, space_required: int, wingspan_cm: int):
        super().__init__(name, age, "meat", space_required, wingspan_cm)
        self.hunt_skill = random.randint(70, 100)

    def get_info(self) -> str:
        return (
            f"{self.name} is a raptor with a {self.wingspan_cm}cm wingspan "
            f"and hunt skill {self.hunt_skill}."
        )


# ---------------------------------------------------------------------------
# Concrete species (leaf classes)
# ---------------------------------------------------------------------------

class Kangaroo(Marsupial):
    """Eastern Grey Kangaroo — the icon of OzZoo."""

    def __init__(self, name: str, age: int = 3):
        super().__init__(name, age, food_type="grass",
                         space_required=4, fur_colour="grey")

    def make_sound(self) -> str:
        return f"{self.name} thumps the ground loudly!"

    def eat(self, food_amount: int) -> str:
        self._hunger = max(0, self._hunger - food_amount * 8)
        self._happiness = min(100, self._happiness + 3)
        return f"{self.name} grazes on {food_amount} units of grass. Nom nom."


class Koala(Marsupial):
    """Koala — sleepy eucalyptus specialist."""

    def __init__(self, name: str, age: int = 4):
        super().__init__(name, age, food_type="eucalyptus",
                         space_required=2, fur_colour="grey-brown")
        self.sleep_hours = 20   # koalas sleep a lot

    def make_sound(self) -> str:
        return f"{self.name} lets out a surprisingly deep bellow!"

    def eat(self, food_amount: int) -> str:
        self._hunger = max(0, self._hunger - food_amount * 6)
        self._happiness = min(100, self._happiness + 5)
        return f"{self.name} munches {food_amount} units of eucalyptus leaves. Crunch."


class Wombat(Marsupial):
    """Wombat — chunky burrower, surprisingly fast."""

    def __init__(self, name: str, age: int = 2):
        super().__init__(name, age, food_type="grass",
                         space_required=3, fur_colour="brown")

    def make_sound(self) -> str:
        return f"{self.name} grunts aggressively!"

    def eat(self, food_amount: int) -> str:
        self._hunger = max(0, self._hunger - food_amount * 7)
        self._happiness = min(100, self._happiness + 4)
        return f"{self.name} chomps {food_amount} units of grass roots. Grunt."


class TasmanianDevil(Carnivore):
    """Tasmanian Devil — loud, fierce, conservation-critical."""

    def __init__(self, name: str, age: int = 2):
        super().__init__(name, age, space_required=3, fur_colour="black")

    def make_sound(self) -> str:
        return f"{self.name} lets out a bloodcurdling screech!!!"

    def eat(self, food_amount: int) -> str:
        self._hunger = max(0, self._hunger - food_amount * 10)
        self._happiness = min(100, self._happiness + 6)
        return f"{self.name} tears into {food_amount} units of meat. SCREECH."


class Dingo(Carnivore):
    """Dingo — Australia's wild dog."""

    def __init__(self, name: str, age: int = 3):
        super().__init__(name, age, space_required=4, fur_colour="sandy-yellow")

    def make_sound(self) -> str:
        return f"{self.name} howls into the night!"

    def eat(self, food_amount: int) -> str:
        self._hunger = max(0, self._hunger - food_amount * 9)
        self._happiness = min(100, self._happiness + 5)
        return f"{self.name} devours {food_amount} units of meat. Howl."


class WedgeTailedEagle(RaptorBird):
    """Wedge-tailed Eagle — Australia's largest bird of prey."""

    def __init__(self, name: str, age: int = 5):
        super().__init__(name, age, space_required=5, wingspan_cm=230)

    def make_sound(self) -> str:
        return f"{self.name} shrieks powerfully from above!"

    def eat(self, food_amount: int) -> str:
        self._hunger = max(0, self._hunger - food_amount * 7)
        self._happiness = min(100, self._happiness + 4)
        return f"{self.name} tears into {food_amount} units of meat with its talons."