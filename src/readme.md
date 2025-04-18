# Developer Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Setup Instructions](#setup-instructions)
5. [Testing](#testing)
6. [Contributing](#contributing)

## Introduction
This document provides guidelines for developers contributing to the Python application. It includes setup instructions, project structure, and best practices.

## Project Structure
#TODO

## Setup Instructions
1. Clone the repository:
    ```bash
    git clone <repository-url>
    ```
2. Navigate to the project directory:
    ```bash
    cd <project-directory>
    ```
3. (Optional) Create a virtual environment:
    ```bash
    python -m venv venv
    ```
4. (Optional) Activate the virtual environment:
    - On Windows:
      ```bash
      venv\Scripts\activate
      ```
    - On macOS/Linux:
      ```bash
      source venv/bin/activate
      ```
5. Install dependencies:
    ```bash
    pip install .
    ```


## Testing (Not Implemented Yet)
Run tests using:
```bash
pytest
```
Ensure all tests pass before submitting a pull request.

## Contributing

1. Remember to add all necessary python libraries to the pyproject.toml
2. If you change the pyproject.toml, remember to run ```bash pip install .``` afterwards or your changes won't take effect


