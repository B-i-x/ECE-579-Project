import random
from typing import List


class Menu:
    """Holds the available items on the menu."""
    mains = ["Burger", "Pizza", "Salad"]
    sides = ["Fries", "Onion Rings", "Coleslaw", "Side Salad", "Mozzarella Sticks"]
    drink = ["Soda", "Lemonade", "Sweet Tea", "Water"]


class Order:
    """Represents a single customer order."""
    def __init__(self):
        self.main = self._choose_main()
        self.sides = self._choose_sides()
        self.drink = self._choose_drink()

    def _choose_main(self) -> str:
        """Randomly choose one main dish."""
        choice = random.choice(Menu.mains)
        print(f"[DEBUG] Chosen main: {choice}")
        return choice

    def _choose_sides(self) -> List[str]:
        """Randomly choose 0 to 2 distinct sides."""
        num_sides = random.randint(0, 2)
        print(f"[DEBUG] Number of sides to choose: {num_sides}")
        choices = random.sample(Menu.sides, k=num_sides)
        print(f"[DEBUG] Chosen sides: {choices}")
        return choices
    
    def _choose_drink(self) -> str:
        """Randomly choose 0 to 1 drinks."""
        num_sides = random.randint(0, 1)
        print(f"[DEBUG] Drink number selected: {num_sides}")
        choice = random.sample(Menu.drink, k=num_sides)
        print(f"[DEBUG] Chosen drink: {choice}")
        return choice

    def __str__(self) -> str:
        sides_str = ", ".join(self.sides) if self.sides else "No sides"
        return f"Main: {self.main} | Sides: {sides_str}"


class OrderGenerator:
    """Generates multiple random orders."""
    def __init__(self, num_orders):
        self.num_orders = num_orders

    def generate_orders(self):
        return [Order() for _ in range(self.num_orders)]


