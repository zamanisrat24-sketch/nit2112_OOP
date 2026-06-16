[README.md](https://github.com/user-attachments/files/28993815/README.md)
# 🦘 OzZoo — Australian Wildlife Park Manager

> A turn-based CLI simulation game in which you manage an Australian zoo, balance a budget, keep animals healthy, and grow your reputation before Day 30.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [File Structure](#file-structure)
3. [How to Run](#how-to-run)
4. [Gameplay Guide](#gameplay-guide)
5. [Architecture & Design Patterns](#architecture--design-patterns)
   - [Factory Method — `factory.py`](#1-factory-method--factorypy)
   - [Observer + Singleton — `observer.py`](#2-observer--singleton--observerpy)
   - [Decorator — `resources.py`](#3-decorator--resourcespy)
6. [OOP Principles Demonstrated](#oop-principles-demonstrated)
   - [Abstraction](#abstraction)
   - [Encapsulation](#encapsulation)
   - [Inheritance](#inheritance)
   - [Polymorphism](#polymorphism)
7. [Class Hierarchy](#class-hierarchy)
8. [Module Reference](#module-reference)
9. [Custom Exception Hierarchy](#custom-exception-hierarchy)
10. [Win & Lose Conditions](#win--lose-conditions)

---

## Project Overview

OzZoo is a menu-driven Python simulation that puts you in charge of an Australian wildlife park. Each menu selection represents one manager action; advancing the day triggers a full simulation tick that updates animal welfare, degrades enclosures, simulates visitor arrivals, fires random events, and checks win/lose conditions.

The project is structured to demonstrate all four pillars of object-oriented programming across a rich, multi-layered class hierarchy, along with three classic Gang-of-Four design patterns applied in contexts where they genuinely improve the design.

---

## File Structure

```
OzZoo/
├── main.py              # Game loop, CLI menu, all action handlers
├── zoo.py               # Central Zoo class — the simulation engine
├── animals.py           # 4-level animal class hierarchy (ABC → species)
├── resources.py         # Enclosure, Food, Medicine, Decorator pattern
├── factory.py           # AnimalFactory — Factory Method pattern
├── observer.py          # HealthMonitor (Singleton) + Observer pattern
├── visitors_events.py   # Visitor satisfaction model + random ZooEvents
└── exceptions.py        # Custom exception hierarchy (7 types)
```

---

## How to Run

**Requirements:** Python 3.10 or later (uses `match` syntax and `X | Y` type union hints).

```bash
python main.py
```

No third-party libraries are required. All modules are part of the standard library (`abc`, `random`).

---

## Gameplay Guide

### Starting Out

When you launch the game you will be asked to name your zoo. You begin with **$8,000** and an empty park. The recommended opening sequence is:

1. **Option 12 — Build enclosure.** Build a `grassland` enclosure with capacity 8 (cost: $900).
2. **Option 8 — Buy animal.** Purchase two Kangaroos (~$800 each).
3. **Option 9 — Buy food.** Stock up on at least 30 units of `grass` ($60 total).
4. **Option 2 — Advance day.** Let the simulation tick and collect ticket revenue.
5. **Feed daily** (option 3 or 4) — hungry animals lose health fast.

### The Manager Menu

| # | Action | Notes |
|---|--------|-------|
| 1 | View zoo status | Full snapshot: budget, reputation, animals, enclosures |
| 2 | Advance to next day | Triggers the full simulation tick |
| 3 | Feed ALL animals | Auto-selects correct food per animal |
| 4 | Feed ONE animal | Choose species and food units manually |
| 5 | Treat sick animal | Administer antibiotics or vitamins |
| 6 | Attempt breeding | Requires 2+ healthy same-species animals |
| 7 | Trigger special behaviour | Species-specific actions (leap, soar, burrow…) |
| 8 | Buy animal | From the catalogue; placed immediately into an enclosure |
| 9 | Buy food | Grass, meat, or eucalyptus |
| 10 | Buy medicine | Antibiotics (+30 HP) or vitamins (+15 HP) |
| 11 | View animal catalogue | Prices and habitat compatibility |
| 12 | Build enclosure | grassland / forest / aviary / scrubland |
| 13 | Clean enclosure | Restores cleanliness to 100% |
| 14 | Upgrade enclosure | Heated / Enrichment / Viewing Platform |
| 15 | Set ticket price | Affects visitor numbers and revenue |
| 0 | Quit | |

### Animals & Habitats

| Species | Habitat | Food | Space | Price |
|---------|---------|------|-------|-------|
| Kangaroo | grassland | grass | 4 | $800 |
| Koala | forest | eucalyptus | 2 | $1,200 |
| Wombat | grassland / forest / scrubland | grass | 3 | $600 |
| Tasmanian Devil | scrubland | meat | 3 | $900 |
| Dingo | grassland / scrubland | meat | 4 | $700 |
| Wedge-tailed Eagle | aviary | meat | 5 | $1,500 |

### Enclosure Upgrades

| Upgrade | Cost | Effect |
|---------|------|--------|
| Heated Habitat | $800 | Cleanliness decays 30% slower |
| Enrichment | $400 | All residents gain +3 happiness/day |
| Viewing Platform | $600 | +10 visitor satisfaction per visit |

### Random Events

Every day there is a 35% chance of a random event. Events can boost or drain the budget, affect all animals' health, or hit enclosure cleanliness. Examples include Heatwave (−15 animal health), Government Grant (+$700), Overnight Storm (−45 enclosure cleanliness), and Viral Social Media Post (+$600).

---

## Architecture & Design Patterns

### 1. Factory Method — `factory.py`

**Problem being solved:** Without a factory, every piece of code that creates an animal must import the concrete class, know its constructor signature, and hard-code the species name. Adding a new species requires finding and updating every creation site.

**Solution:** `AnimalFactory` keeps all species metadata — class reference and purchase price — in a single `CATALOGUE` dictionary. The `create()` classmethod is completely generic; it never names an individual species. Adding a new animal to the game requires only one line in `CATALOGUE`.

```python
# All callers look like this — species name is the only variable
animal = AnimalFactory.create("kangaroo", "Bindi")
price  = AnimalFactory.get_price("wedgetailedeagle")
```

The factory also normalises species keys (strips spaces, hyphens, case) so that `"Tasmanian Devil"`, `"tasmaniandevil"`, and `"tasmanian-devil"` all resolve correctly. A `register_species()` classmethod allows new species to be added at runtime without modifying any existing code — an open/closed principle win.

---

### 2. Observer + Singleton — `observer.py`

**Problem being solved:** Animals need to raise health alerts visible to the manager, but the `Animal` class should know nothing about the `Zoo`, the CLI, or any alert channel. Coupling `Animal` to `Zoo` would violate the Single Responsibility Principle.

**Observer solution:** `HealthMonitor` is the *subject*. Each tick it scans all animals and calls `_notify()` when a critical condition is detected. Any class implementing the `HealthObserver` ABC can subscribe and receive those alerts without `Animal` or `HealthMonitor` knowing what those classes do.

Two concrete observers ship with the game:

- `ManagerAlertObserver` — queues alerts to display at the end of each tick, then clears the queue (`flush_alerts()`).
- `LogObserver` — accumulates a permanent chronological log shown in the end-game summary.

Adding a new alert channel (email, push notification, GUI pop-up) requires only a new `HealthObserver` subclass and a single `register()` call — no changes to `Animal` or `HealthMonitor`.

**Singleton solution:** There must be exactly one `HealthMonitor` for the zoo. Multiple instances would send duplicate alerts and maintain inconsistent "already alerted" tracking. The classic `__new__` override guarantees only one instance is ever created. A `reset()` classmethod lets tests and new game sessions start clean.

---

### 3. Decorator — `resources.py`

**Problem being solved:** Enclosures can receive up to three independent upgrades — Heated Habitat, Enrichment, and Viewing Platform. Using subclassing would require a class for every possible combination (`HeatedEnriched`, `HeatedPlatform`, `HeatedEnrichedPlatform`, etc.) — seven classes for three upgrades.

**Solution:** `EnclosureDecorator` wraps any `ICleanable` (either a bare `Enclosure` or another decorator) and delegates all interface calls by default. Each concrete decorator overrides only the method it augments:

```
Enclosure (concrete component)
    ↓  wrapped by
HeatedHabitatDecorator     → degrade_cleanliness() 30% slower
    ↓  wrapped by
EnrichmentDecorator        → all animals +3 happiness per tick
    ↓  wrapped by
ViewingPlatformDecorator   → visitor satisfaction +10
```

All three upgrades compose freely. The `Zoo` class stores the outermost decorator in `self.enclosures` and interacts with it through the shared `ICleanable` interface, so the zoo is never aware of which decorators are stacked.

---

## OOP Principles Demonstrated

### Abstraction

Two abstract base classes define contracts that all implementors must honour:

- **`Animal` (ABC)** — declares `make_sound()`, `eat()`, and `get_info()` as `@abstractmethod`. No concrete `Animal` instance can be created; the factory always returns a species subclass.
- **`ICleanable` (ABC)** — declares `clean()` and `get_cleanliness()`. Both `Enclosure` and `EnclosureDecorator` implement this interface, enabling the `Zoo` to manage them polymorphically.
- **`HealthObserver` (ABC)** — declares `on_critical_health()`. All alert subscribers must implement this single method.

### Encapsulation

All welfare statistics on `Animal` are stored as protected attributes (`_health`, `_hunger`, `_happiness`, `_energy`) and exposed via read-only `@property` decorators. Direct external mutation is prevented; updates flow through methods like `heal()`, `boost_happiness()`, and `update_stats()`, which enforce valid ranges and side-effects. Similarly, `Enclosure._cleanliness` is only modified via `degrade_cleanliness()` and `clean()`, keeping the invariant that it stays within 0–100.

### Inheritance

The animal class hierarchy is four levels deep:

```
Animal (ABC)                          ← Level 1
├── Mammal                            ← Level 2  (+fur_colour, groom())
│   ├── Marsupial                     ← Level 3  (+pouch_young)
│   │   ├── Kangaroo                  ← Level 4  (leap())
│   │   ├── Koala                     ← Level 4  (nap())
│   │   └── Wombat                    ← Level 4  (burrow())
│   └── Carnivore                     ← Level 3  (+prey_drive)
│       ├── TasmanianDevil            ← Level 4  (display_aggression())
│       └── Dingo                     ← Level 4  (patrol())
└── Bird                              ← Level 2  (+wingspan_cm, perch())
    └── RaptorBird                    ← Level 3  (+hunt_skill)
        └── WedgeTailedEagle          ← Level 4  (soar())
```

The exception hierarchy mirrors this pattern — all custom exceptions inherit from `ZooException`, allowing callers to catch broadly or precisely.

### Polymorphism

Polymorphism is demonstrated at every layer:

- **`animal.eat(units)`** — the `Zoo` calls this on any `Animal` reference; the actual eating logic dispatched is species-specific (Kangaroo consumes 8 hunger/unit, Koala 6, TasmanianDevil 10, etc.).
- **`animal.make_sound()`** — unique vocalisation string per species.
- **`enc.update()`** — whether `enc` is a bare `Enclosure` or a stack of decorators, calling `update()` triggers the correct chain of behaviours.
- **`enc.clean()` / `enc.get_cleanliness()`** — the `Zoo` calls these through the `ICleanable` interface, regardless of decorator depth.

---

## Class Hierarchy

See the companion `OzZoo_UML.puml` file for the full PlantUML class diagram. The top-level relationships are:

- `Zoo` **uses** `AnimalFactory` (Factory Method)
- `Zoo` **owns** a list of `Enclosure` / `EnclosureDecorator`
- `Zoo` **owns** `HealthMonitor` (Singleton) and registers two `HealthObserver` instances
- `Enclosure` **contains** a list of `Animal` instances
- `EnclosureDecorator` **wraps** any `ICleanable`
- All concrete animal species inherit from `Animal` through the four-level hierarchy

---

## Module Reference

### `animals.py`
Defines the full 10-class animal hierarchy. `Animal` is the ABC; `Mammal` and `Bird` are level-2 intermediates; `Marsupial`, `Carnivore`, and `RaptorBird` are level-3 intermediates; `Kangaroo`, `Koala`, `Wombat`, `TasmanianDevil`, `Dingo`, and `WedgeTailedEagle` are the concrete leaf species. Shared welfare logic (`update_stats`, `heal`, `boost_happiness`, `can_breed`, `is_critical`) lives in `Animal` and is inherited by all species.

### `resources.py`
Contains `ICleanable` (interface ABC), `Enclosure` (concrete component), `EnclosureDecorator` (abstract wrapper), and the three concrete decorators. Also contains `Food` (inventory unit for a specific food type) and `Medicine` (inventory unit for a specific medicine type with a `treat()` method).

### `factory.py`
`AnimalFactory` with a `CATALOGUE` class attribute mapping species keys to `(class, price)` tuples. Public API: `create()`, `get_price()`, `get_species_class()`, `list_available()`, `register_species()`.

### `observer.py`
`HealthObserver` (ABC interface), `ManagerAlertObserver`, `LogObserver`, and `HealthMonitor` (Singleton subject). The monitor's `check_animals()` method deduplicates alerts via a `_previously_critical` set to avoid spamming the same warning every tick.

### `visitors_events.py`
`Visitor` — models a single zoo visitor with a satisfaction score that responds to animal happiness and enclosure cleanliness. High-satisfaction visitors may make a voluntary donation. `ZooEvent` — random events drawn from a `EVENT_POOL` of 12 entries, each with an `effect_type` (`finance`, `animal`, or `enclosure`) and a `magnitude`.

### `zoo.py`
`Zoo` — the central orchestrator. Manages finances, enclosures, food/medicine stock, and the daily `tick()`. Delegates animal creation to `AnimalFactory`, applies decorator upgrades, wires up the Observer pattern on `__init__`, and checks win/lose conditions at the end of every tick.

### `exceptions.py`
Seven custom exception classes all inheriting from `ZooException`. Enables precise error handling throughout the codebase without relying on generic built-in exceptions.

### `main.py`
One handler function per menu option, a `print_menu()` display function, and `game_loop()` which dispatches user input to the correct handler via an `actions` dict keyed by menu number.

---

## Custom Exception Hierarchy

```
ZooException (base)
├── InsufficientFundsError      — purchase cannot be made
├── HabitatCapacityError        — enclosure has no space
├── IncompatibleSpeciesError    — species doesn't suit this habitat
├── InsufficientFoodError       — food stock exhausted
├── AnimalDeathError            — action on an already-dead animal
├── InvalidActionError          — logically invalid game action
└── DuplicateEnclosureError     — enclosure ID already exists
```

---

## Win & Lose Conditions

**Win** (all four required simultaneously by Day 30):

| Condition | Target |
|-----------|--------|
| Day reached | ≥ 30 |
| Budget | ≥ $10,000 |
| Living animals | ≥ 5 |
| Reputation | ≥ 60 / 100 |

**Lose:** Budget drops below $0 at any point.

Reputation is earned by purchasing animals (+2), applying upgrades (+3), successful breeding (+5), and keeping visitors satisfied (+2 per tick when average satisfaction ≥ 75). Animal deaths cost −5 reputation each.
