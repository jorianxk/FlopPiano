#!/bin/bash

# The path to the python virtual environment is the current install.sh directory
# + "/env"
env_dir="$(realpath $(dirname $0))/env"

# String helper
install_str="[FlopPiano Install]:"

# Create the python virtual environment
echo "$install_str Creating environment in $env_dir..."
python3 -m venv $env_dir
echo "$install_str Done."

# Activate the python virtual environment to install required packages
echo "$install_str Activating environment..."
source "$env_dir/bin/activate"
echo "$install_str Done."

# Install dependencies 
echo "$install_str Installing dependency mido[ports-rtmidi]..."
pip install mido[ports-rtmidi]
echo "$install_str Done."

echo "$install_str Installing dependency asciimatics..."
pip install asciimatics
echo "$install_str Done."
