#!/bin/bash

while true; do
    # ===============
    python ~test1.py
    # ===============
    
    # Check the exit status of the Python script
    if [ $? -eq 0 ]; then
        echo "Script completed successfully."
        break  # Exit the loop if successful
    else
        echo "Script failed. Restarting..."
        sleep 1  # Optional: Sleep for a few seconds before restarting
    fi
done
