#!/bin/bash

# Create project directories
mkdir -p src/{producer,consumer,utils,monitoring}
mkdir -p data/{raw,processed}
mkdir -p models
mkdir -p docker
mkdir -p tests
mkdir -p notebooks

# Create empty __init__.py files
touch src/__init__.py
touch src/producer/__init__.py
touch src/consumer/__init__.py
touch src/utils/__init__.py
touch src/monitoring/__init__.py

# Create .gitkeep files for empty directories
touch data/raw/.gitkeep
touch data/processed/.gitkeep
touch models/.gitkeep 