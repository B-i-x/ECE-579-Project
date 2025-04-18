import argparse
# from src.foodie_ai.simulation import run_simulation


def parse_args():
    parser = argparse.ArgumentParser(description="Run the FOODIE delivery simulation.")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
