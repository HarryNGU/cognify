#!/bin/bash

# Setup virtual environment
echo "Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install required packages
echo "Installing required packages..."
pip install flask spacy networkx beautifulsoup4

# Download spaCy model
echo "Downloading spaCy model..."
python -m spacy download en_core_web_sm

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p src/uploads src/processed src/knowledge_maps src/learning_journeys src/static

# Run the application
echo "Starting the Knowledge Map application..."
cd src
python app.py
