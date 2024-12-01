#!/bin/bash

# Define macros for Git URL, Personal Access Token (PAT), and branch name
LEBENCH_GIT_URL="https://github.com/Psml03/LEBench.git"
LEBENCHMARK_GIT_URL="https://github.com/Psml03/LEBenchmark.git"
GITPAT="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"
GIT_BRANCH="spectrev2"

# Define the directories and output file path
LEBENCH_DIR="/mnt/purnya/benchmark/LEBench"
OUTPUT_FILE="/mnt/purnya/benchmark/LEBenchoutput.6.1.0-26-amd64.csv"
DEST_DIR="/mnt/purnya/benchmark/LEBenchmark"

# Run the loop 12 times
for i in {1..12}; do
    echo "Starting iteration $i..."

    # Navigate to LEBench
    cd "$LEBENCH_DIR"
    if [ $? -ne 0 ]; then
        echo "Failed to navigate to $LEBENCH_DIR. Exiting."
        exit 1
    fi

    # Run the required scripts
    sudo taskset -c 0-5,24-29 python3 get_kern.py
    if [ $? -ne 0 ]; then
        echo "Error running get_kern.py. Exiting."
        exit 1
    fi

    sudo taskset -c 0-5,24-29 python3 run.py
    if [ $? -ne 0 ]; then
        echo "Error running run.py. Exiting."
        exit 1
    fi

    # Commit and push changes in LEBench
    git add .
    git commit -m "Run $i Spectre V2 Kernel"
    git push origin "$GIT_BRANCH"

    # Move the output file to the destination directory
    if [ -f "$OUTPUT_FILE" ]; then
        mv -f "$OUTPUT_FILE" "$DEST_DIR"
        if [ $? -ne 0 ]; then
            echo "Failed to move $OUTPUT_FILE to $DEST_DIR. Exiting."
            exit 1
        fi
    else
        echo "Output file $OUTPUT_FILE not found. Skipping move operation."
    fi

    # Commit and push changes in LEBenchmark
    cd "$DEST_DIR"
    if [ $? -ne 0 ]; then
        echo "Failed to navigate to $DEST_DIR. Exiting."
        exit 1
    fi

    git add .
    git commit -m "Run $i Spectre V2 Kernel"
    git push origin "$GIT_BRANCH"

    echo "Completed iteration $i."

    # Wait for 1 minute before proceeding to the next iteration
    if [ $i -lt 12 ]; then
        echo "Waiting for 1 minute before the next iteration..."
        sleep 60
    fi
done

echo "All iterations completed."
