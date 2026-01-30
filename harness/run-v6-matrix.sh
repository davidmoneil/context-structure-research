#!/bin/bash
#
# Full matrix test for V6 structures
# Tests all 23 questions × 4 structures × 2 loading methods = 184 tests
#
# Structures:
# - flat-v6 (base flat)
# - deep-v6 (base nested)
# - flat-v6-v5.5 (flat + keywords/summaries)
# - deep-v6-v5.5 (nested + keywords/summaries)

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
RESULTS_DIR="$PROJECT_ROOT/results/v6-matrix/raw"

mkdir -p "$RESULTS_DIR/haiku"

LOG_FILE="$PROJECT_ROOT/results/v6-matrix/full-matrix-$(date +%Y%m%d-%H%M%S).log"
mkdir -p "$(dirname "$LOG_FILE")"

# Structures to test
# Start with base structures, then add enhanced if they exist
STRUCTURES=("flat-v6" "deep-v6")

# Add enhanced structures if build completed
if [ -d "$PROJECT_ROOT/soong-daystrom/flat-v6-v5.5" ]; then
    STRUCTURES+=("flat-v6-v5.5")
fi
if [ -d "$PROJECT_ROOT/soong-daystrom/deep-v6-v5.5" ]; then
    STRUCTURES+=("deep-v6-v5.5")
fi

# Loading methods
LOADING_METHODS=("classic" "adddir")

# Get all question IDs
QUESTIONS=$(jq -r '.[].id' "$PROJECT_ROOT/harness/questions.json")
QUESTION_COUNT=$(echo "$QUESTIONS" | wc -l)

TOTAL=$((QUESTION_COUNT * ${#STRUCTURES[@]} * ${#LOADING_METHODS[@]}))
COMPLETED=0
START_TIME=$(date +%s)

echo "==================================================="
echo "  V6 Full Matrix Test"
echo "==================================================="
echo ""
echo "Questions: $QUESTION_COUNT"
echo "Structures: ${STRUCTURES[*]}"
echo "Loading methods: ${LOADING_METHODS[*]}"
echo "Total tests: $TOTAL"
echo ""
echo "Start: $(date)"
echo "---------------------------------------------------"

exec > >(tee -a "$LOG_FILE") 2>&1

for STRUCTURE in "${STRUCTURES[@]}"; do
    for LOADING in "${LOADING_METHODS[@]}"; do
        echo ""
        echo "[$STRUCTURE / $LOADING]"

        for QID in $QUESTIONS; do
            COMPLETED=$((COMPLETED + 1))

            OUTPUT_FILE="$RESULTS_DIR/haiku/${STRUCTURE}_${LOADING}_100_${QID}.json"

            # Skip if exists
            if [ -f "$OUTPUT_FILE" ]; then
                printf "  [%3d/%d] %-18s %-7s %-10s ... ⏭ (exists)\n" "$COMPLETED" "$TOTAL" "$STRUCTURE" "$LOADING" "$QID"
                continue
            fi

            printf "  [%3d/%d] %-18s %-7s %-10s ... " "$COMPLETED" "$TOTAL" "$STRUCTURE" "$LOADING" "$QID"

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
done

END_TIME=$(date +%s)
DURATION=$(( (END_TIME - START_TIME) / 60 ))

echo ""
echo "==================================================="
echo "  V6 Full Matrix Complete"
echo "==================================================="
echo "  Total tests: $TOTAL"
echo "  Duration: $DURATION minutes"
echo "  Results: $RESULTS_DIR"
echo "==================================================="
