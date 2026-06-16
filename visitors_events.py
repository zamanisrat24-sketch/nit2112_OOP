"""
visitors_events.py - Visitor and ZooEvent classes for OzZoo.
"""

import random


class Visitor:
    """
    Represents a zoo visitor.

    Satisfaction is driven by animal health and enclosure cleanliness.
    Happy visitors pay more and may donate.

    Attributes:
        visitor_id (int): Unique ID.
        _satisfaction (int): 0-100, starts at 60.
        admission_paid (float): Admission fee this visitor paid.
    """

    _id_counter = 0

    def __init__(self, admission_fee: float):
        Visitor._id_counter += 1
        self.visitor_id = Visitor._id_counter
        self._satisfaction = 60
        self.admission_paid = admission_fee

    @property
    def satisfaction(self) -> int:
        return self._satisfaction

    def observe_animal(self, animal_happiness: int):
        """
        Watching a happy, healthy animal boosts visitor satisfaction.

        Args:
            animal_happiness (int): The observed animal's happiness score.
        """
        if animal_happiness >= 80:
            self._satisfaction = min(100, self._satisfaction + 5)
        elif animal_happiness < 40:
            self._satisfaction = max(0, self._satisfaction - 8)

    def observe_enclosure(self, cleanliness: int):
        """
        Dirty enclosures reduce satisfaction; clean ones boost it.

        Args:
            cleanliness (int): Enclosure cleanliness 0-100.
        """
        if cleanliness >= 70:
            self._satisfaction = min(100, self._satisfaction + 3)
        elif cleanliness < 40:
            self._satisfaction = max(0, self._satisfaction - 10)

    def maybe_donate(self) -> float:
        """
        Highly satisfied visitors may make a donation.

        Returns:
            float: Donation amount (0 if they don't donate).
        """
        if self._satisfaction >= 85:
            donation = round(random.uniform(10, 100), 2)
            return donation
        return 0.0

    def __str__(self):
        return f"Visitor #{self.visitor_id} | Satisfaction: {self._satisfaction}"


class ZooEvent:
    """
    Represents a random event that occurs during the game.

    Events add unpredictability and force the player to adapt.

    Attributes:
        name (str): Event name.
        description (str): Flavour text shown to the player.
        effect_type (str): Category of effect ('finance', 'animal', 'enclosure').
        magnitude (int): Strength of the effect (positive or negative).
    """

    # Pool of possible events: (name, description, effect_type, magnitude)
    EVENT_POOL = [
        (
            "Heatwave 🌡️",
            "A scorching heatwave hits OzZoo! Enclosures heat up and animals suffer.",
            "animal", -15
        ),
        (
            "Viral Social Post 📱",
            "A visitor's video of your koala went viral! Ticket sales surge.",
            "finance", 500
        ),
        (
            "Animal Birth 🐣",
            "One of your marsupials has given birth to a joey! Public interest soars.",
            "finance", 300
        ),
        (
            "Plumbing Leak 🔧",
            "A burst pipe floods two enclosures. Emergency repairs needed.",
            "finance", -400
        ),
        (
            "Wildlife Donation 🎁",
            "A conservation group donates food supplies worth $200.",
            "finance", 200
        ),
        (
            "Sick Animal 🤒",
            "A sudden illness is spreading among your animals. Health drops.",
            "animal", -20
        ),
        (
            "School Excursion 🎒",
            "A large school group arrives! Extra ticket revenue today.",
            "finance", 350
        ),
        (
            "Storm Damage ⛈️",
            "An overnight storm damaged an enclosure. Cleanliness plummets.",
            "enclosure", -40
        ),
    ]

    def __init__(self, name: str, description: str,
                 effect_type: str, magnitude: int):
        self.name = name
        self.description = description
        self.effect_type = effect_type
        self.magnitude = magnitude

    @classmethod
    def random_event(cls) -> "ZooEvent":
        """Pick and return a random event from the pool."""
        e = random.choice(cls.EVENT_POOL)
        return cls(*e)

    @classmethod
    def maybe_trigger(cls, chance: float = 0.35) -> "ZooEvent | None":
        """
        Randomly decide whether an event fires this tick.

        Args:
            chance (float): Probability 0-1 that an event occurs.

        Returns:
            ZooEvent or None.
        """
        if random.random() < chance:
            return cls.random_event()
        return None

    def __str__(self):
        sign = "+" if self.magnitude > 0 else ""
        return f"{self.name}: {self.description} (Effect: {sign}{self.magnitude})"