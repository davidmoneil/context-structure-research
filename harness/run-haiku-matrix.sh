#!/bin/bash
#
# Run full Haiku test matrix
# 5 structures × 2 loading methods × 23 questions = 230 tests
#

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Parse version argument
VERSION="${1:-}"
if [[ -z "$VERSION" ]]; then
    echo "Usage: $0 <version>"
    echo "  version: v1, v2, v3, v4, etc."
    exit 1
fi

# Set versioned paths
RESULTS_DIR="$PROJECT_ROOT/results/$VERSION/raw"
LOG_FILE="$PROJECT_ROOT/results/$VERSION/haiku-matrix-$(date +%Y%m%d-%H%M%S).log"
mkdir -p "$RESULTS_DIR/haiku"

STRUCTURES=("monolith" "flat" "shallow" "deep" "very-deep")
LOADING_METHODS=("classic" "adddir")
QUESTIONS=$(jq -r '.[].id' "$SCRIPT_DIR/questions.json")
QUESTION_COUNT=$(echo "$QUESTIONS" | wc -l)

TOTAL=$((5 * 2 * QUESTION_COUNT))
COMPLETED=0
SKIPPED=0
FAILED=0
START_TIME=$(date +%s)

echo "==================================================="
echo "  Context Structure Research - Haiku Full Matrix"
echo "  Corpus Version: $VERSION"
echo "==================================================="
echo ""
echo "Configuration:"
echo "  Structures: ${STRUCTURES[*]}"
echo "  Loading: ${LOADING_METHODS[*]}"
echo "  Questions: $QUESTION_COUNT"
echo "  Total tests: $TOTAL"
echo "  Results dir: $RESULTS_DIR"
echo ""
echo "Log file: $LOG_FILE"
echo ""
echo "Starting at $(date)"
echo "---------------------------------------------------"

mkdir -p "$(dirname "$LOG_FILE")"

{
    echo "Haiku Matrix Run - $(date)"
    echo "Total tests: $TOTAL"
    echo ""
} >> "$LOG_FILE"

for structure in "${STRUCTURES[@]}"; do
    for loading in "${LOADING_METHODS[@]}"; do
        echo ""
        echo "[$structure / $loading]"
        
        for qid in $QUESTIONS; do
            COMPLETED=$((COMPLETED + 1))
            ELAPSED=$(($(date +%s) - START_TIME))
            
            if [[ $COMPLETED -gt 1 ]]; then
                AVG_TIME=$((ELAPSED / (COMPLETED - 1)))
                REMAINING=$(( (TOTAL - COMPLETED + 1) * AVG_TIME ))
                ETA_MIN=$((REMAINING / 60))
            else
                ETA_MIN="?"
            fi
            
            # Check if result already exists (resume support)
            RESULT_FILE="$RESULTS_DIR/haiku/${structure}_${loading}_100_${qid}.json"
            if [[ -f "$RESULT_FILE" ]]; then
                printf "  [%3d/%d] %-8s %-7s %-10s ... " \
                    "$COMPLETED" "$TOTAL" "$structure" "$loading" "$qid"
                echo "⏭ (exists)"
                SKIPPED=$((SKIPPED + 1))
                continue
            fi

            printf "  [%3d/%d] %-8s %-7s %-10s (ETA: %s min)... " \
                "$COMPLETED" "$TOTAL" "$structure" "$loading" "$qid" "$ETA_MIN"

            if "$SCRIPT_DIR/run-test.sh" --structure "$structure" --question "$qid" --loading "$loading" --results-dir "$RESULTS_DIR" >> "$LOG_FILE" 2>&1; then
                echo "✓"
            else
                echo "✗"
                FAILED=$((FAILED + 1))
                echo "FAILED: $structure/$loading/$qid" >> "$LOG_FILE"
            fi
        done
    done
done

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
DURATION_MIN=$((DURATION / 60))

echo ""
echo "==================================================="
echo "  Complete!"
echo "==================================================="
echo "  Total: $TOTAL"
echo "  Skipped (already done): $SKIPPED"
echo "  Ran this session: $((COMPLETED - SKIPPED))"
echo "  Failed: $FAILED"
echo "  Duration: ${DURATION_MIN} minutes"
echo "  Results: $RESULTS_DIR/haiku/"
echo ""

# Generate summary
TOTAL_COST=$(cat "$RESULTS_DIR/haiku/"*.json 2>/dev/null | jq -r '.response' | jq -r '.total_cost_usd // 0' 2>/dev/null | awk '{sum += $1} END {printf "%.2f", sum}')
echo "  Total cost: \$${TOTAL_COST}"
echo ""

{
    echo ""
    echo "=== Run Complete ==="
    echo "Duration: ${DURATION_MIN} minutes"
    echo "Successful: $((COMPLETED - FAILED))/$TOTAL"
    echo "Failed: $FAILED"
    echo "Total cost: \$${TOTAL_COST}"
} >> "$LOG_FILE"
