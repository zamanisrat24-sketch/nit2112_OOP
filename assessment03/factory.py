"""
factory.py - AnimalFactory using the Factory design pattern.

Design Pattern: Factory Method
Why: Instead of scattering animal constructors across the codebase,
     all creation goes through one place. Adding a new species only
     requires registering it here — nothing else changes.
"""

from animals import (
    Animal, Kangaroo, Koala, Wombat,
    TasmanianDevil, Dingo, WedgeTailedEagle
)


class AnimalFactory:
    """
    Factory class for creating Animal instances by species name.

    Usage:
        animal = AnimalFactory.create("kangaroo", "Bindi")
        animal = AnimalFactory.create("koala", "Gumnut", age=6)

    Attributes:
        CATALOGUE (dict): Maps species key → (class, base_price).
    """

    CATALOGUE: dict = {
        "kangaroo":         (Kangaroo,          800),
        "koala":            (Koala,             1200),
        "wombat":           (Wombat,             600),
        "tasmaniandevil":   (TasmanianDevil,     900),
        "dingo":            (Dingo,              700),
        "wedgetailedeagle": (WedgeTailedEagle,  1500),
    }

    @classmethod
    def create(cls, species: str, name: str, age: int = None) -> Animal:
        """
        Create and return an Animal of the requested species.

        Args:
            species (str): Species key (case-insensitive, no spaces).
            name (str): The animal's individual name.
            age (int, optional): Age in years. Uses class default if omitted.

        Returns:
            Animal: A fully initialised animal instance.

        Raises:
            ValueError: If species is not in the catalogue.
        """
        key = species.lower().replace(" ", "").replace("-", "")
        if key not in cls.CATALOGUE:
            available = ", ".join(cls.CATALOGUE.keys())
            raise ValueError(
                f"Unknown species '{species}'. Available: {available}"
            )

        animal_class, _ = cls.CATALOGUE[key]

        if age is not None:
            return animal_class(name, age)
        return animal_class(name)

    @classmethod
    def get_price(cls, species: str) -> int:
        """
        Return the purchase price for a given species.

        Args:
            species (str): Species key.

        Returns:
            int: Price in dollars.

        Raises:
            ValueError: If species is not in the catalogue.
        """
        key = species.lower().replace(" ", "").replace("-", "")
        if key not in cls.CATALOGUE:
            raise ValueError(f"Unknown species '{species}'.")
        _, price = cls.CATALOGUE[key]
        return price

    @classmethod
    def list_available(cls) -> str:
        """Return a formatted string listing all purchasable species and prices."""
        lines = ["Available animals to purchase:"]
        for key, (animal_class, price) in cls.CATALOGUE.items():
            lines.append(f"  {key:<20} ${price}")
        return "\n".join(lines)