#!/bin/bash

#The installtion directory of FlopPiano is the directry of this script
install_dir="$(realpath $(dirname $0))"

# Change to the FlopPiano directory
cd $install_dir

# Activate the python environment
source "env/bin/activate"

# Run the entry point of floppiano, pass along any arguments
python -m "floppiano.main" "$@"
