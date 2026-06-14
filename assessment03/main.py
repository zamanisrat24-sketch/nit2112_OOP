"""
main.py - Game loop and CLI for OzZoo simulation.

The CLI is menu-driven. Each iteration of the main loop represents
one manager action. The player advances the day when ready.
"""

from zoo import Zoo
from factory import AnimalFactory
from exceptions import (
    InsufficientFundsError, HabitatCapacityError,
    IncompatibleSpeciesError, InsufficientFoodError, ZooException
)


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def clear_screen():
    """Print blank lines to simulate a screen clear in any terminal."""
    print("\n" * 3)


def print_header():
    print("=" * 50)
    print("   🦘  O z Z o o  —  Wildlife Park Manager  🦅")
    print("=" * 50)


def print_menu():
    print("""
┌─────────────────────────────────────┐
│           MANAGER MENU              │
├─────────────────────────────────────┤
│  1. View zoo status                 │
│  2. Advance to next day             │
│  3. Feed all animals                │
│  4. Buy animal                      │
│  5. Buy food                        │
│  6. Buy medicine                    │
│  7. Build enclosure                 │
│  8. Clean enclosure                 │
│  9. Treat sick animal               │
│ 10. Attempt breeding                │
│ 11. Set ticket price                │
│ 12. View animal catalogue           │
│  0. Quit                            │
└─────────────────────────────────────┘""")


def prompt(text: str) -> str:
    """Standard input prompt with consistent formatting."""
    return input(f"  >> {text}: ").strip()


def pause():
    input("\n  [Press Enter to continue]")


# ---------------------------------------------------------------------------
# Action handlers — one function per menu option
# ---------------------------------------------------------------------------

def action_status(zoo: Zoo):
    print(zoo.status_report())
    pause()


def action_advance_day(zoo: Zoo):
    print("\n  Advancing to the next day...\n")
    log = zoo.tick()
    for line in log:
        print(line)
    pause()


def action_feed_all(zoo: Zoo):
    print("\n  Feeding all animals...\n")
    try:
        messages = zoo.feed_all()
        for msg in messages:
            print(f"  {msg}")
    except InsufficientFoodError as e:
        print(f"  ⚠️  Food shortage: {e}")
    pause()


def action_buy_animal(zoo: Zoo):
    print(f"\n{AnimalFactory.list_available()}")
    if not zoo.enclosures:
        print("\n  ⚠️  You have no enclosures yet. Build one first (option 7).")
        pause()
        return

    print("\n  Your enclosures:")
    for enc in zoo.enclosures:
        print(f"    {enc.status_summary()}")

    species = prompt("Species to buy (or blank to cancel)").lower()
    if not species:
        return
    name = prompt("Name for the animal")
    if not name:
        return
    enc_id = prompt("Enclosure ID to place it in")

    try:
        result = zoo.buy_animal(species, name, enc_id)
        print(f"\n  ✅ {result}")
    except (InsufficientFundsError, HabitatCapacityError,
            IncompatibleSpeciesError, ValueError) as e:
        print(f"\n  ❌ {e}")
    pause()


def action_buy_food(zoo: Zoo):
    print("\n  Food types: grass ($2/unit), meat ($5/unit), eucalyptus ($4/unit)")
    print(f"  Budget: ${zoo.budget:.2f}\n")
    food_type = prompt("Food type (or blank to cancel)").lower()
    if not food_type:
        return
    try:
        amount = int(prompt("How many units"))
        result = zoo.buy_food(food_type, amount)
        print(f"\n  ✅ {result}")
    except InsufficientFundsError as e:
        print(f"\n  ❌ {e}")
    except ValueError as e:
        print(f"\n  ❌ Invalid input: {e}")
    pause()


def action_buy_medicine(zoo: Zoo):
    print("\n  Medicine: antibiotics ($10/dose, +30 health) | vitamins ($5/dose, +15 health)")
    print(f"  Budget: ${zoo.budget:.2f}\n")
    med_type = prompt("Medicine type (or blank to cancel)").lower()
    if not med_type:
        return
    try:
        amount = int(prompt("How many doses"))
        result = zoo.buy_medicine(med_type, amount)
        print(f"\n  ✅ {result}")
    except InsufficientFundsError as e:
        print(f"\n  ❌ {e}")
    except ValueError as e:
        print(f"\n  ❌ Invalid input: {e}")
    pause()


def action_build_enclosure(zoo: Zoo):
    print("\n  Habitat types: grassland, forest, aviary, scrubland")
    print("  Cost: $500 base + $50 per capacity unit\n")
    enc_id = prompt("Enclosure ID (e.g. G2)")
    if not enc_id:
        return
    habitat = prompt("Habitat type").lower()
    try:
        capacity = int(prompt("Capacity (space units)"))
        result = zoo.build_enclosure(enc_id, habitat, capacity)
        print(f"\n  ✅ {result}")
    except InsufficientFundsError as e:
        print(f"\n  ❌ {e}")
    except ValueError as e:
        print(f"\n  ❌ {e}")
    pause()


def action_clean_enclosure(zoo: Zoo):
    if not zoo.enclosures:
        print("\n  No enclosures to clean.")
        pause()
        return
    print("\n  Enclosures:")
    for enc in zoo.enclosures:
        print(f"    {enc.status_summary()}")
    enc_id = prompt("Enclosure ID to clean (or blank to cancel)")
    if not enc_id:
        return
    result = zoo.clean_enclosure(enc_id)
    print(f"\n  ✅ {result}")
    pause()


def action_treat_animal(zoo: Zoo):
    animals = zoo.all_animals()
    if not animals:
        print("\n  No animals in the zoo.")
        pause()
        return
    print("\n  Animals:")
    for a in animals:
        print(f"    {a.status_summary()}")
    print(f"\n  Medicine stock:")
    for med in zoo.medicine_stock.values():
        print(f"    {med}")
    name = prompt("Animal name to treat (or blank to cancel)")
    if not name:
        return
    med_type = prompt("Medicine type")
    result = zoo.treat_animal(name, med_type)
    print(f"\n  {result}")
    pause()


def action_breeding(zoo: Zoo):
    if not zoo.enclosures:
        print("\n  No enclosures built yet.")
        pause()
        return
    print("\n  Enclosures:")
    for enc in zoo.enclosures:
        print(f"    {enc.status_summary()}")
    enc_id = prompt("Enclosure ID to attempt breeding in (or blank to cancel)")
    if not enc_id:
        return
    result = zoo.attempt_breeding(enc_id)
    print(f"\n  {result}")
    pause()


def action_set_ticket_price(zoo: Zoo):
    print(f"\n  Current ticket price: ${zoo.ticket_price:.2f}")
    try:
        price = float(prompt("New ticket price"))
        result = zoo.set_ticket_price(price)
        print(f"\n  ✅ {result}")
    except ValueError:
        print("\n  ❌ Please enter a valid number.")
    pause()


def action_catalogue():
    print(f"\n{AnimalFactory.list_available()}")
    print("""
  Habitat compatibility:
    grassland  → Kangaroo, Wombat, Dingo
    forest     → Koala, Wombat
    aviary     → WedgeTailedEagle
    scrubland  → TasmanianDevil, Dingo, Wombat
""")
    pause()


# ---------------------------------------------------------------------------
# New game setup
# ---------------------------------------------------------------------------

def setup_new_game() -> Zoo:
    """Walk the player through naming their zoo and starting setup."""
    clear_screen()
    print_header()
    print("""
  G'day, Manager! Welcome to OzZoo.
  The previous manager left quite suddenly
  (something about a wombat incident...).

  It's up to YOU to build a world-class wildlife park.
  Balance your budget, keep the animals happy,
  and make the visitors love it!
""")
    zoo_name = prompt("What will you name your zoo? (default: OzZoo)")
    if not zoo_name:
        zoo_name = "OzZoo"

    zoo = Zoo(name=zoo_name, starting_budget=8000.0)

    print(f"""
  Great! {zoo_name} starts with $8,000.
  Tip: Build an enclosure first, then buy animals.
  Feed your animals every day or their health will drop!
""")
    pause()
    return zoo


# ---------------------------------------------------------------------------
# Main game loop
# ---------------------------------------------------------------------------

def game_loop(zoo: Zoo):
    """Central game loop. Runs until player quits or goes bankrupt."""
    actions = {
        "1":  action_status,
        "2":  action_advance_day,
        "3":  action_feed_all,
        "4":  action_buy_animal,
        "5":  action_buy_food,
        "6":  action_buy_medicine,
        "7":  action_build_enclosure,
        "8":  action_clean_enclosure,
        "9":  action_treat_animal,
        "10": action_breeding,
        "11": action_set_ticket_price,
    }

    while not zoo.game_over:
        clear_screen()
        print_header()
        print(f"\n  Day: {zoo.day} | Budget: ${zoo.budget:.2f} | "
              f"Animals: {len(zoo.all_animals())} | "
              f"Enclosures: {len(zoo.enclosures)}")
        print_menu()

        choice = prompt("Choose an option").strip()

        if choice == "0":
            print("\n  Thanks for playing OzZoo! See ya later, mate. 🦘")
            break
        elif choice == "12":
            action_catalogue()
        elif choice in actions:
            try:
                actions[choice](zoo)
            except ZooException as e:
                # Catch any unhandled zoo-level exception at the top level
                print(f"\n  ❌ Zoo error: {e}")
                pause()
            except Exception as e:
                print(f"\n  ❌ Unexpected error: {e}")
                pause()
        else:
            print("\n  ❌ Invalid option. Please choose 0-12.")
            pause()

    if zoo.game_over:
        print("\n" + "=" * 50)
        print("  💸 GAME OVER — OzZoo has gone bankrupt!")
        print(f"  You survived {zoo.day} days.")
        print("=" * 50)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    zoo = setup_new_game()
    game_loop(zoo)