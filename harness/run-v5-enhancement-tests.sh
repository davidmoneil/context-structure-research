#!/bin/bash
#
# Run targeted tests on V5 enhancements for failed questions
# Tests V5.1-V5.4 variants on questions that failed in baseline
#

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
RESULTS_DIR="$PROJECT_ROOT/results/v5-enhancements/raw"

# Which variant to test (passed as argument)
VARIANT="${1:-v5.1}"
STRUCTURE_BASE="${2:-deep-v5}"  # deep-v5 or flat-v5

STRUCTURE="${STRUCTURE_BASE}-${VARIANT}"
LOG_FILE="$PROJECT_ROOT/results/v5-enhancements/${STRUCTURE}-$(date +%Y%m%d-%H%M%S).log"

mkdir -p "$RESULTS_DIR/haiku"
mkdir -p "$(dirname "$LOG_FILE")"

# Failed questions from V5 baseline to re-test
FAILED_QUESTIONS=("XREF-002" "XREF-003" "XREF-006" "DEPTH-004" "DEPTH-005")

# Loading methods
LOADING_METHODS=("classic" "adddir")

TOTAL=$((${#FAILED_QUESTIONS[@]} * ${#LOADING_METHODS[@]}))
COMPLETED=0
START_TIME=$(date +%s)

echo "==================================================="
echo "  V5 Enhancement Test: $STRUCTURE"
echo "==================================================="
echo ""
echo "Testing ${#FAILED_QUESTIONS[@]} failed questions × ${#LOADING_METHODS[@]} loading methods"
echo "Total tests: $TOTAL"
echo "Results: $RESULTS_DIR"
echo ""
echo "Start: $(date)"
echo "---------------------------------------------------"

exec > >(tee -a "$LOG_FILE") 2>&1

for LOADING in "${LOADING_METHODS[@]}"; do
    echo ""
    echo "[$STRUCTURE / $LOADING]"

    for QID in "${FAILED_QUESTIONS[@]}"; do
        COMPLETED=$((COMPLETED + 1))

        OUTPUT_FILE="$RESULTS_DIR/haiku/${STRUCTURE}_${LOADING}_100_${QID}.json"

        # Skip if exists
        if [ -f "$OUTPUT_FILE" ]; then
            printf "  [%2d/%d] %-20s %-7s %-10s ... ⏭ (exists)\n" "$COMPLETED" "$TOTAL" "$STRUCTURE" "$LOADING" "$QID"
            continue
        fi

        printf "  [%2d/%d] %-20s %-7s %-10s ... " "$COMPLETED" "$TOTAL" "$STRUCTURE" "$LOADING" "$QID"

        if "$SCRIPT_DIR/run-test.sh" \
            --structure "$STRUCTURE" \
            --question "$QID" \
            --loading "$LOADING" \
            --results-dir "$RESULTS_DIR" \
            >> "$LOG_FILE.detail" 2>&1; then
            echo "✓"
        else
            echo "✗"
        fi
    done
done

echo ""
echo "==================================================="
echo "  $STRUCTURE Tests Complete"
echo "==================================================="
echo "  Total: $TOTAL"
echo "  Duration: $(( ($(date +%s) - START_TIME) / 60 )) minutes"
echo "==================================================="
