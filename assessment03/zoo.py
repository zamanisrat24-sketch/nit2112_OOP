"""
zoo.py - The central Zoo class for OzZoo simulation.

The Zoo owns all enclosures, tracks finances, manages food/medicine
inventory, processes each game tick, and applies random events.
"""

import random
from animals import Animal
from resources import Enclosure, Food, Medicine
from factory import AnimalFactory
from visitors_events import Visitor, ZooEvent
from observer import HealthMonitor, ManagerAlertObserver, LogObserver
from exceptions import (
    InsufficientFundsError, HabitatCapacityError,
    IncompatibleSpeciesError, InsufficientFoodError
)


class Zoo:
    """
    Central management class for OzZoo.

    Responsibilities:
        - Track finances (budget).
        - Maintain enclosures and their animals.
        - Manage food and medicine inventory.
        - Process daily ticks (update all entities, apply events).
        - Handle visitor income and satisfaction.
        - Provide information methods for the CLI to display.

    Attributes:
        name (str): Zoo name.
        budget (float): Current funds in dollars.
        day (int): Current game day.
        ticket_price (float): Daily admission fee per visitor.
        enclosures (list[Enclosure]): All enclosures.
        food_stock (dict[str, Food]): food_type → Food object.
        medicine_stock (dict[str, Medicine]): type → Medicine object.
        daily_log (list[str]): Messages generated during the last tick.
        game_over (bool): True if the player has lost.
    """

    def __init__(self, name: str = "OzZoo", starting_budget: float = 8000.0):
        self.name = name
        self.budget = starting_budget
        self.day = 0
        self.ticket_price = 25.0
        self.enclosures: list[Enclosure] = []
        self.food_stock: dict[str, Food] = {
            "grass":       Food("grass",       30, 2.0),
            "meat":        Food("meat",        20, 5.0),
            "eucalyptus":  Food("eucalyptus",  15, 4.0),
        }
        self.medicine_stock: dict[str, Medicine] = {
            "antibiotics": Medicine("antibiotics", 5, 30, 10.0),
            "vitamins":    Medicine("vitamins",    5, 15,  5.0),
        }
        self.daily_log: list[str] = []
        self.game_over: bool = False
        self.won: bool = False

        # Observer pattern
        self.alert_observer = ManagerAlertObserver()
        self.log_observer = LogObserver()
        self.health_monitor = HealthMonitor()
        self.health_monitor.register(self.alert_observer)
        self.health_monitor.register(self.log_observer)

        # Win condition: day 30, budget > $10k, 5+ animals
        self.WIN_DAY = 30
        self.WIN_BUDGET = 10_000
        self.WIN_ANIMALS = 5

    # ------------------------------------------------------------------
    # Properties / helpers
    # ------------------------------------------------------------------

    def all_animals(self) -> list[Animal]:
        """Return a flat list of all living animals across all enclosures."""
        animals = []
        for enc in self.enclosures:
            animals.extend(a for a in enc.animals if a.is_alive)
        return animals

    def get_enclosure(self, enc_id: str) -> Enclosure | None:
        """Find an enclosure by its ID (case-insensitive)."""
        for enc in self.enclosures:
            if enc.enclosure_id.lower() == enc_id.lower():
                return enc
        return None

    def get_animal(self, name: str) -> Animal | None:
        """Find a living animal by name (case-insensitive)."""
        for animal in self.all_animals():
            if animal.name.lower() == name.lower():
                return animal
        return None

    # ------------------------------------------------------------------
    # Purchase actions
    # ------------------------------------------------------------------

    def buy_animal(self, species: str, name: str, enclosure_id: str) -> str:
        """
        Purchase a new animal and place it in an enclosure.

        Args:
            species (str): Species key for AnimalFactory.
            name (str): Name for the new animal.
            enclosure_id (str): Target enclosure ID.

        Returns:
            str: Result message.

        Raises:
            InsufficientFundsError: If budget is too low.
            HabitatCapacityError: If enclosure is full.
            IncompatibleSpeciesError: If species doesn't match habitat.
        """
        price = AnimalFactory.get_price(species)
        if self.budget < price:
            raise InsufficientFundsError(
                f"Cannot afford {species} (${price}). Budget: ${self.budget:.2f}"
            )

        enc = self.get_enclosure(enclosure_id)
        if enc is None:
            return f"Enclosure '{enclosure_id}' not found."

        animal = AnimalFactory.create(species, name)
        enc.add_animal(animal)   # may raise Habitat/Incompatible errors
        self.budget -= price
        return (
            f"Purchased {animal.name} the {species} for ${price}. "
            f"Budget remaining: ${self.budget:.2f}"
        )

    def buy_food(self, food_type: str, amount: int) -> str:
        """
        Purchase food and add to inventory.

        Args:
            food_type (str): 'grass', 'meat', or 'eucalyptus'.
            amount (int): Units to buy.

        Returns:
            str: Result message.

        Raises:
            InsufficientFundsError: If budget is too low.
            ValueError: If food_type is invalid.
        """
        if food_type not in self.food_stock:
            raise ValueError(f"Unknown food type '{food_type}'.")
        food = self.food_stock[food_type]
        cost = food.cost_per_unit * amount
        if self.budget < cost:
            raise InsufficientFundsError(
                f"Cannot afford {amount} units of {food_type} (${cost:.2f}). "
                f"Budget: ${self.budget:.2f}"
            )
        food.restock(amount)
        self.budget -= cost
        return (
            f"Bought {amount} units of {food_type} for ${cost:.2f}. "
            f"Stock now: {food.quantity}. Budget: ${self.budget:.2f}"
        )

    def buy_medicine(self, medicine_type: str, amount: int) -> str:
        """
        Purchase medicine and add to inventory.

        Args:
            medicine_type (str): 'antibiotics' or 'vitamins'.
            amount (int): Doses to buy.

        Returns:
            str: Result message.

        Raises:
            InsufficientFundsError: If budget is too low.
        """
        if medicine_type not in self.medicine_stock:
            raise ValueError(f"Unknown medicine '{medicine_type}'.")
        med = self.medicine_stock[medicine_type]
        cost = med.cost_per_dose * amount
        if self.budget < cost:
            raise InsufficientFundsError(
                f"Cannot afford {amount} doses of {medicine_type} (${cost:.2f})."
            )
        med.quantity += amount
        self.budget -= cost
        return (
            f"Bought {amount} doses of {medicine_type} for ${cost:.2f}. "
            f"Budget: ${self.budget:.2f}"
        )

    def build_enclosure(self, enc_id: str, habitat_type: str, capacity: int) -> str:
        """
        Build a new enclosure. Costs $500 + $50 per capacity unit.

        Args:
            enc_id (str): Unique ID for the enclosure.
            habitat_type (str): Habitat type.
            capacity (int): Space units.

        Returns:
            str: Result message.

        Raises:
            InsufficientFundsError: If budget is too low.
        """
        cost = 500 + (capacity * 50)
        if self.budget < cost:
            raise InsufficientFundsError(
                f"Cannot afford enclosure (${cost}). Budget: ${self.budget:.2f}"
            )
        if self.get_enclosure(enc_id):
            return f"An enclosure with ID '{enc_id}' already exists."
        enc = Enclosure(enc_id, habitat_type, capacity)
        self.enclosures.append(enc)
        self.budget -= cost
        return (
            f"Built '{enc_id}' ({habitat_type}, capacity {capacity}) for ${cost}. "
            f"Budget: ${self.budget:.2f}"
        )

    # ------------------------------------------------------------------
    # Management actions
    # ------------------------------------------------------------------

    def feed_all(self) -> list[str]:
        """
        Feed every living animal from inventory. Auto-selects correct food type.

        Returns:
            list[str]: Feed result messages.
        """
        messages = []
        for animal in self.all_animals():
            food = self.food_stock.get(animal.food_type)
            if food is None or food.quantity <= 0:
                messages.append(
                    f"⚠️  No {animal.food_type} for {animal.name}! "
                    f"Hunger increases."
                )
                continue
            consumed = food.consume(3)
            if consumed == 0:
                raise InsufficientFoodError(
                    f"Food stock for {animal.food_type} is empty!"
                )
            messages.append(animal.eat(consumed))
        return messages

    def treat_animal(self, animal_name: str, medicine_type: str) -> str:
        """
        Administer medicine to a named animal.

        Args:
            animal_name (str): Name of the animal to treat.
            medicine_type (str): Type of medicine to use.

        Returns:
            str: Result message.
        """
        animal = self.get_animal(animal_name)
        if animal is None:
            return f"No living animal named '{animal_name}' found."
        med = self.medicine_stock.get(medicine_type)
        if med is None:
            return f"Unknown medicine '{medicine_type}'."
        return med.treat(animal)

    def clean_enclosure(self, enc_id: str) -> str:
        """Clean an enclosure by ID."""
        enc = self.get_enclosure(enc_id)
        if enc is None:
            return f"Enclosure '{enc_id}' not found."
        return enc.clean()

    def set_ticket_price(self, price: float) -> str:
        """Set admission ticket price."""
        if price < 0:
            return "Ticket price cannot be negative."
        self.ticket_price = price
        return f"Ticket price set to ${price:.2f}."

    def attempt_breeding(self, enc_id: str) -> str:
        """
        Attempt breeding in an enclosure if conditions are met.
        Requires 2+ healthy animals of the same species.

        Args:
            enc_id (str): Enclosure to check.

        Returns:
            str: Result message.
        """
        enc = self.get_enclosure(enc_id)
        if enc is None:
            return f"Enclosure '{enc_id}' not found."

        living = [a for a in enc.animals if a.is_alive and a.can_breed()]
        species_count: dict[str, list] = {}
        for animal in living:
            species = animal.__class__.__name__
            species_count.setdefault(species, []).append(animal)

        for species, group in species_count.items():
            if len(group) >= 2:
                # A joey is born — represented as a finance/happiness boost
                self.budget += 200   # public interest boost
                for a in group:
                    a._happiness = min(100, a._happiness + 10)
                return (
                    f"🐣 A new {species} joey was born in '{enc_id}'! "
                    f"Public excitement adds $200 to the budget."
                )
        return "No compatible breeding pairs found in this enclosure."

    # ------------------------------------------------------------------
    # Game tick
    # ------------------------------------------------------------------

    def tick(self) -> list[str]:
        """
        Advance the simulation by one day.

        Steps:
            1. Increment day counter.
            2. Update all animals (hunger, health).
            3. Update all enclosures (cleanliness).
            4. Simulate visitor arrivals and income.
            5. Maybe trigger a random event.
            6. Check win/lose conditions.

        Returns:
            list[str]: Log of everything that happened this tick.
        """
        self.day += 1
        log = [f"\n{'='*50}", f"  DAY {self.day} — {self.name}", f"{'='*50}"]

        # 1. Update animals
        for animal in self.all_animals():
            animal.update_stats()
            if animal.is_critical():
                log.append(f"🔴 ALERT: {animal.name} is in critical health!")
            if not animal.is_alive:
                log.append(f"💀 {animal.name} has died.")

        # 2. Update enclosures
        for enc in self.enclosures:
            enc.update()

        # 3. Visitors
        visitor_count = self._calculate_visitors()
        income = round(visitor_count * self.ticket_price, 2)
        donations = 0.0
        for _ in range(visitor_count):
            v = Visitor(self.ticket_price)
            for enc in self.enclosures:
                v.observe_enclosure(enc.get_cleanliness())
                for animal in enc.animals:
                    if animal.is_alive:
                        v.observe_animal(animal.happiness)
            donations += v.maybe_donate()

        donations = round(donations, 2)
        self.budget += income + donations
        log.append(f"👥 {visitor_count} visitors arrived. Income: ${income} | Donations: ${donations}")

        # 4. Observer — health monitor checks all animals
        self.health_monitor.check_animals(self.all_animals())
        alerts = self.alert_observer.flush_alerts()
        log.extend(alerts)

        # 5. Random event
        event = ZooEvent.maybe_trigger()
        if event:
            log.append(f"\n⚡ EVENT: {event}")
            self._apply_event(event, log)

        # 6. Budget summary
        log.append(f"💰 Budget: ${self.budget:.2f}")

        # 7. Win condition check
        if (self.day >= self.WIN_DAY
                and self.budget >= self.WIN_BUDGET
                and len(self.all_animals()) >= self.WIN_ANIMALS):
            self.won = True
            self.game_over = True
            log.append(
                f"\n🏆 YOU WIN! OzZoo is a world-class wildlife park! "
                f"Day {self.day} | Budget: ${self.budget:.2f} | "
                f"Animals: {len(self.all_animals())}"
            )

        # 8. Bankruptcy check
        elif self.budget < 0:
            self.game_over = True
            log.append("\n❌ GAME OVER: You've run out of money. OzZoo is bankrupt!")

        self.daily_log = log
        return log

    def _calculate_visitors(self) -> int:
        """
        Calculate visitor count based on animal happiness and cleanliness.
        More happy animals and clean enclosures attract more visitors.
        """
        base = 20
        animals = self.all_animals()
        if not animals:
            return max(5, base // 2)

        avg_happiness = sum(a.happiness for a in animals) / len(animals)
        avg_clean = (
            sum(e.get_cleanliness() for e in self.enclosures) / len(self.enclosures)
            if self.enclosures else 50
        )

        # Scale visitors based on zoo quality
        multiplier = (avg_happiness + avg_clean) / 200  # 0.0 – 1.0
        visitors = int(base + (multiplier * 40)) + random.randint(-3, 3)
        return max(1, visitors)

    def _apply_event(self, event: ZooEvent, log: list[str]):
        """Apply a ZooEvent's effect to the zoo."""
        if event.effect_type == "finance":
            self.budget += event.magnitude
            change = f"+${event.magnitude}" if event.magnitude > 0 else f"-${abs(event.magnitude)}"
            log.append(f"  💵 Budget change: {change}")

        elif event.effect_type == "animal":
            for animal in self.all_animals():
                animal._health = max(0, animal._health + event.magnitude)
            log.append(f"  🐾 All animal health changed by {event.magnitude}.")

        elif event.effect_type == "enclosure":
            for enc in self.enclosures:
                enc._cleanliness = max(0, enc._cleanliness + event.magnitude)
            log.append(f"  🏚️  All enclosure cleanliness changed by {event.magnitude}.")

    # ------------------------------------------------------------------
    # Status displays
    # ------------------------------------------------------------------

    def status_report(self) -> str:
        """Full zoo status for CLI display."""
        lines = [
            f"\n{'─'*50}",
            f"  {self.name} — Day {self.day}",
            f"  Budget: ${self.budget:.2f} | Ticket: ${self.ticket_price:.2f}",
            f"  🎯 WIN GOAL: Day {self.WIN_DAY} | ${self.WIN_BUDGET:,} budget | {self.WIN_ANIMALS}+ animals",
            f"{'─'*50}",
            "\nENCLOSURES:",
        ]
        if not self.enclosures:
            lines.append("  No enclosures built yet.")
        else:
            for enc in self.enclosures:
                lines.append(f"  {enc.status_summary()}")

        lines.append("\nANIMALS:")
        animals = self.all_animals()
        if not animals:
            lines.append("  No animals in the zoo.")
        else:
            for a in animals:
                lines.append(f"  {a.status_summary()}")

        lines.append("\nFOOD STOCK:")
        for food in self.food_stock.values():
            lines.append(f"  {food}")

        lines.append("\nMEDICINE STOCK:")
        for med in self.medicine_stock.values():
            lines.append(f"  {med}")

        return "\n".join(lines)