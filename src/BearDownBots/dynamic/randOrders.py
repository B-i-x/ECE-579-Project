import random
from typing import List


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


class Order:
    """Represents a single customer order."""
    def __init__(self, building, print_debug=False):
        self.print_debug = print_debug
        self.main = self._choose_main()
        self.sides = self._choose_sides()
        self.drink = self._choose_drink()

        self.building = building

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

    def __str__(self) -> str:
        sides_str = ", ".join(self.sides) if self.sides else "No sides"
        drink_str = "".join(self.drink) if self.drink else "No drink"
        return f"Main: {self.main} | Sides: {sides_str} | Drink: {drink_str}"



