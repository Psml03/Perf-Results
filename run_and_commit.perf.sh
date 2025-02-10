#!/bin/bash


# Define benchmark directories and output file path
LEBENCH_DIR=""
PERF_DIR=""

# Run the loop for 7 iterations
for i in {1..7}; do
    echo "Starting iteration $i..."

    # Navigate to LEBench directory
    cd "$LEBENCH_DIR" || { echo "Failed to navigate to $LEBENCH_DIR. 
Exiting."; exit 1; }

    # Run benchmark scripts with CPU pinning
    sudo taskset -c 0-11,24-35 python3 get_kern.py
    if [ $? -ne 0 ]; then
        echo "Error running get_kern.py. Exiting."
        exit 1
    fi

    sudo taskset -c 0-11,24-35 python3 run.py
    if [ $? -ne 0 ]; then
        echo "Error running run.py. Exiting."
        exit 1
    fi

    # Commit and push changes to the Perf repository
    cd "$PERF_DIR" || { echo "Failed to navigate to $PERF_DIR. Exiting."; exit 1; }
    git add .
    git commit -m "Run $i"
    git push 
    rm -f debug_log.txt

    echo "Completed iteration $i."

    # Wait 1 minute before the next iteration 
    if [ $i -lt 7 ]; then
        echo "Waiting for 1 minute before the next iteration..."
        sleep 60
    fi
done

echo "All iterations completed."

