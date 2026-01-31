#!/bin/bash
# Run extended V6 test matrix with parallel execution (2 workers)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
RESULTS_DIR="$PROJECT_ROOT/results/v6-extended/raw/haiku"
PARALLEL_JOBS=2

# Test configuration
STRUCTURES=("shallow-v6" "very-deep-v6")
LOADING_METHODS=("classic" "adddir")
MODEL="haiku"

# Create results directory
mkdir -p "$RESULTS_DIR"

echo "================================================"
echo "  V6 Extended Matrix Test (Parallel: $PARALLEL_JOBS)"
echo "================================================"
echo "Structures: ${STRUCTURES[*]}"
echo "Methods: ${LOADING_METHODS[*]}"
echo "Model: $MODEL"
echo "Results: $RESULTS_DIR"
echo ""

# Build list of all test combinations
TESTS_FILE=$(mktemp)
for structure in "${STRUCTURES[@]}"; do
    CORPUS_DIR="$PROJECT_ROOT/soong-daystrom/$structure"
    if [ ! -d "$CORPUS_DIR" ]; then
        echo "ERROR: Structure not found: $CORPUS_DIR"
        exit 1
    fi

    for method in "${LOADING_METHODS[@]}"; do
        for question_id in $(jq -r '.[].id' "$SCRIPT_DIR/questions.json"); do
            OUTPUT_FILE="$RESULTS_DIR/${structure}_${method}_100_${question_id}.json"
            # Skip if already exists
            if [ ! -f "$OUTPUT_FILE" ]; then
                echo "$structure $method $question_id" >> "$TESTS_FILE"
            fi
        done
    done
done

TOTAL_TESTS=$(wc -l < "$TESTS_FILE")
echo "Tests to run: $TOTAL_TESTS (skipping cached)"
echo ""

if [ "$TOTAL_TESTS" -eq 0 ]; then
    echo "All tests already cached!"
    rm "$TESTS_FILE"
    exit 0
fi

START_TIME=$(date +%s)
COMPLETED=0
LOCK_FILE=$(mktemp)

run_test() {
    local structure=$1
    local method=$2
    local question_id=$3

    OUTPUT_FILE="$RESULTS_DIR/${structure}_${method}_100_${question_id}.json"

    if "$SCRIPT_DIR/run-test.sh" \
        --structure "$structure" \
        --question "$question_id" \
        --loading "$method" \
        --model "$MODEL" \
        --results-dir "$RESULTS_DIR" > /dev/null 2>&1; then
        echo "✓ $structure $method $question_id"
    else
        echo "✗ $structure $method $question_id"
    fi
}

export -f run_test
export SCRIPT_DIR RESULTS_DIR MODEL

# Run tests with GNU parallel (2 jobs)
if command -v parallel &> /dev/null; then
    cat "$TESTS_FILE" | parallel -j $PARALLEL_JOBS --colsep ' ' run_test {1} {2} {3}
else
    # Fallback: simple background job approach
    echo "GNU parallel not found, using background jobs..."

    while IFS=' ' read -r structure method question_id; do
        # Wait if we have $PARALLEL_JOBS running
        while [ $(jobs -r | wc -l) -ge $PARALLEL_JOBS ]; do
            sleep 1
        done

        run_test "$structure" "$method" "$question_id" &
    done < "$TESTS_FILE"

    # Wait for remaining jobs
    wait
fi

rm "$TESTS_FILE"

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
MINUTES=$((DURATION / 60))

FINAL_COUNT=$(ls "$RESULTS_DIR" 2>/dev/null | wc -l)

echo ""
echo "================================================"
echo "  V6 Extended Matrix Complete"
echo "================================================"
echo "  Tests completed: $FINAL_COUNT"
echo "  Duration: $MINUTES minutes"
echo "  Results: $RESULTS_DIR"
echo "================================================"
