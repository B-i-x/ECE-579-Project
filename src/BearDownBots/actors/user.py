class User:

    def __init__(self):
        self.time = 0

    def play(self):
        """
        Main loop for the user.
        """
        self.time += 1
        print(f"[DEBUG] User time: {self.time}")