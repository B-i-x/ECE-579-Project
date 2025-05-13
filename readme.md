# ECE-579 Project

## Team Members
- **Eli Jacobson**
- **Vai Pujary**
- **Alex Romero**
- **Derek Kropp**

## Project Description
BearDownBots is an AI-driven expert system that orchestrates a fleet of three constant‑speed robots to deliver meals for the Bear Express restaurant across a configurable university campus. The system procedurally generates a bounded map (using maze‑generation techniques to place obstacles) and simulates random food orders arriving every 10 minutes from diverse campus locations.

Operating from a central food warehouse, each robot loads multiple orders and services several destinations before returning to resupply. Through adjustable parameters (e.g. map size, robot speed, buffer assumptions) and advanced path‑planning and scheduling algorithms, BearDownBots minimizes average delivery time per item while enabling concurrent, intelligent coordination across all robots.

## How to Run
1. Clone the repository

2. Navigate to the project directory:
    ```bash
    cd ECE-579-Project
    ```
3. Install dependencies:
    ```bash
    pip install -e .
    ```
4. Run the project:
    ```bash
    run
    ```

    or if you want to run a smaller campus map for development
    ``bash
    run-fast
    ```


## Repository Structure
- `/src`: Source code
- `/tests`: Test cases
- `/assets`: Pictures and other assets

## Contributing

1. Remember to add all necessary python libraries to the pyproject.toml


## License
Include license information here.
