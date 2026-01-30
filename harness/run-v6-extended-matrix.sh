#!/bin/bash
# Run extended V6 test matrix: shallow-v6 and very-deep-v6

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
RESULTS_DIR="$PROJECT_ROOT/results/v6-extended/raw/haiku"

# Test configuration
STRUCTURES=("shallow-v6" "very-deep-v6")
LOADING_METHODS=("classic" "adddir")
MODEL="haiku"

# Create results directory
mkdir -p "$RESULTS_DIR"

echo "================================================"
echo "  V6 Extended Matrix Test"
echo "================================================"
echo "Structures: ${STRUCTURES[*]}"
echo "Methods: ${LOADING_METHODS[*]}"
echo "Model: $MODEL"
echo "Results: $RESULTS_DIR"
echo ""

# Count total tests
QUESTIONS=$(jq -r '.[].id' "$SCRIPT_DIR/questions.json")
QUESTION_COUNT=$(echo "$QUESTIONS" | wc -l)
TOTAL_TESTS=$((${#STRUCTURES[@]} * ${#LOADING_METHODS[@]} * QUESTION_COUNT))
CURRENT_TEST=0

START_TIME=$(date +%s)

for structure in "${STRUCTURES[@]}"; do
    CORPUS_DIR="$PROJECT_ROOT/soong-daystrom/$structure"

    if [ ! -d "$CORPUS_DIR" ]; then
        echo "ERROR: Structure not found: $CORPUS_DIR"
        echo "Run: ./harness/build-v6-missing-structures.sh first"
        exit 1
    fi

    for method in "${LOADING_METHODS[@]}"; do
        for question_id in $QUESTIONS; do
            CURRENT_TEST=$((CURRENT_TEST + 1))

            # Output file (matches run-test.sh naming: STRUCTURE_LOADING_100_QUESTION.json)
            OUTPUT_FILE="$RESULTS_DIR/${structure}_${method}_100_${question_id}.json"

            # Skip if already exists
            if [ -f "$OUTPUT_FILE" ]; then
                printf "  [%3d/%d] %-20s %-8s %-10s ... (cached)\n" \
                    "$CURRENT_TEST" "$TOTAL_TESTS" "$structure" "$method" "$question_id"
                continue
            fi

            printf "  [%3d/%d] %-20s %-8s %-10s ... " \
                "$CURRENT_TEST" "$TOTAL_TESTS" "$structure" "$method" "$question_id"

            # Run the test
            if "$SCRIPT_DIR/run-test.sh" \
                --structure "$structure" \
                --question "$question_id" \
                --loading "$method" \
                --model "$MODEL" \
                --results-dir "$RESULTS_DIR" > /dev/null 2>&1; then
                echo "✓"
            else
                echo "✗"
            fi
        done
    done
done

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
MINUTES=$((DURATION / 60))

echo ""
echo "================================================"
echo "  V6 Extended Matrix Complete"
echo "================================================"
echo "  Total tests: $TOTAL_TESTS"
echo "  Duration: $MINUTES minutes"
echo "  Results: $RESULTS_DIR"
echo "================================================"
echo ""
echo "To analyze:"
echo "  python3 harness/evaluator.py results/v6-extended/raw/haiku --output results/v6-extended/analysis"
