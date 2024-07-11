#!/bin/bash

#The installtion directory of FlopPiano is the directry of this script
install_dir="$(realpath $(dirname $0))"

# Change to the FlopPiano directory
cd $install_dir

# Activate the python environment
source "env/bin/activate"


# Check if the positional argument 1 is set, if so pass it along to the python
# script
if [[ "$1" ]]; then
    python -m "floppiano.main" "$1"
else
    # Run the FlopPiano entry without arguments
    python -m "floppiano.main"
fi
