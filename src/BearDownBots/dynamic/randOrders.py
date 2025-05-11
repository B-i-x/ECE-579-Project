import random
from typing import List
from dataclasses import dataclass
from enum   import Enum

class Menu:
    """Holds the available items on the menu."""
    mains = [
        # handhelds
        "Burger", "Cheeseburger", "Chicken Sandwich", "Veggie Burger",
        "Grilled Cheese", "Pulled-Pork Sandwich", "BLT",
        # wraps / tacos
        "Chicken Wrap", "Falafel Wrap", "Beef Taco", "Fish Taco",
        # bowls / plates
        "Pizza", "Margherita Pizza", "Pepperoni Pizza",
        "Chicken Alfredo Pasta", "Spaghetti & Meatballs",
        "Chicken Teriyaki Bowl", "Burrito Bowl",
        "Caesar Salad", "Greek Salad", "Cobb Salad"
    ]

    sides = [
        "Fries", "Sweet-Potato Fries", "Onion Rings", "Tater Tots",
        "Potato Wedges", "Mozzarella Sticks", "Garlic Bread",
        "Cole Slaw", "Side Salad", "Fruit Cup", "Mac & Cheese",
        "Chips & Salsa", "Guacamole & Chips", "Cup of Chili",
        "Tomato Soup", "Chicken Noodle Soup", "Steamed Veggies"
    ]

    drinks = [
        # cold
        "Soda", "Diet Soda", "Root Beer", "Lemonade", "Iced Tea",
        "Sweet Tea", "Orange Juice", "Apple Juice", "Sports Drink",
        "Sparkling Water", "Bottled Water",
        # hot
        "Coffee", "Latte", "Cappuccino", "Hot Tea", "Hot Chocolate",
        # specialty
        "Smoothie", "Milkshake", "Iced Coffee"
    ]

class OrderStatus(Enum):
    PLACED = "PLACED"  # just arrived from a building
    PREPARING = "PREPARING"  # kitchen busy – not ready yet
    READY = "READY"  # cooked, still at warehouse
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"  # loaded onto a robot

class Order:
    """Represents a single customer order.
    • `created_at` – simulation-time stamp when it was placed
    • `prep_time`  – how long the kitchen takes (s, *sim-time*)
    • `ready_at`   – `created_at + prep_time`
    """
    def __init__(self, building, created_at: float, print_debug=False):
        self.print_debug = print_debug
        self.created_at = created_at
        self.status = OrderStatus.PLACED

        self.main = self._choose_main()
        self.sides = self._choose_sides()
        self.drink = self._choose_drink()

        self.building = building

        self.prep_time = self._compute_prep_time()  # seconds
        self.ready_at = self.created_at + self.prep_time

    def _choose_main(self) -> str:
        """Randomly choose one main dish."""
        choice = random.choice(Menu.mains)
        if self.print_debug:
            print(f"[DEBUG] Chosen main: {choice}")
        return choice

    def _choose_sides(self) -> List[str]:
        """Randomly choose 0 to 2 distinct sides."""
        num_sides = random.randint(0, 2)
        choices = random.sample(Menu.sides, k=num_sides)
        if self.print_debug:
            print(f"[DEBUG] Chosen sides: {choices}")
        return choices
    
    def _choose_drink(self) -> str:
        """Randomly choose 0 to 1 drinks."""
        if random.randint(0, 1) == 0:
            return None
        choice = random.choice(Menu.drinks)
        if self.print_debug:
            print(f"[DEBUG] Chosen drink: {choice}")
        return choice

    # ────────────────────────────────────────────────────────────────────
    # Kitchen timing helpers
    # ────────────────────────────────────────────────────────────────────

    def _compute_prep_time(self) -> float:
        """
        Very rough model:
        • main dish base time (look-up, else 180 s)
        • +60 s per side
        • +30 s if a drink is included
        • ±15 s random kitchen variability
        """
        BASE_MAIN = {
            # pizzas
            "Pizza": 420, "Margherita Pizza": 420, "Pepperoni Pizza": 420,
            # pastas / bowls
            "Chicken Alfredo Pasta": 360, "Spaghetti & Meatballs": 360,
            "Chicken Teriyaki Bowl": 300, "Burrito Bowl": 300,
            # burgers & handhelds
            "Burger": 240, "Cheeseburger": 240, "Chicken Sandwich": 240,
            "Veggie Burger": 240, "Grilled Cheese": 180, "BLT": 180,
            # salads / wraps / tacos
            "Falafel Wrap": 210, "Beef Taco": 180, "Fish Taco": 210,
            "Caesar Salad": 150, "Greek Salad": 150, "Cobb Salad": 150,
        }

        t = BASE_MAIN.get(self.main, 180)
        t += 60 * len(self.sides)

        if self.drink:
            t += 30
        t += random.randint(-15, 15)
        return max(30, t)  # never < 30 s

    # public helper
    def is_ready(self, now: float) -> bool:
        """True once the kitchen has finished cooking.Also flips `status`
        the **first** time it becomes ready."""
        if now >= self.ready_at and self.status == OrderStatus.PREPARING:
            self.status = OrderStatus.READY
        return now >= self.ready_at

    def __str__(self) -> str:
        status = self.status.value
        sides_str = ", ".join(self.sides) if self.sides else "No sides"
        drink_str = self.drink if self.drink else "No drink"
        return f"[{status}] Main: {self.main} | Sides: {sides_str} | Drink: {drink_str}"


