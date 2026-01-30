#!/bin/bash
#
# Run Haiku test matrix for V5 corpus - SKIPPING MONOLITH
# Monolith-v5 exceeds Haiku's 200K token limit
#

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

VERSION="v5"
RESULTS_DIR="$PROJECT_ROOT/results/$VERSION/raw"
LOG_FILE="$PROJECT_ROOT/results/$VERSION/haiku-matrix-$(date +%Y%m%d-%H%M%S).log"
mkdir -p "$RESULTS_DIR/haiku"

# V5 structures - EXCLUDING monolith-v5 (too large for Haiku context)
STRUCTURES=("flat-v5" "shallow-v5" "deep-v5" "very-deep-v5")
LOADING_METHODS=("classic" "adddir")
QUESTIONS=$(jq -r '.[].id' "$SCRIPT_DIR/questions.json")
QUESTION_COUNT=$(echo "$QUESTIONS" | wc -l)

# 4 structures × 2 loading methods × 23 questions = 184 tests
TOTAL=$((4 * 2 * QUESTION_COUNT))
COMPLETED=0
SKIPPED=0
FAILED=0
START_TIME=$(date +%s)

echo "==================================================="
echo "  Context Structure Research - Haiku V5 Matrix"
echo "  (Skipping monolith - exceeds context limit)"
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

exec > >(tee -a "$LOG_FILE") 2>&1

for STRUCTURE in "${STRUCTURES[@]}"; do
  for LOADING in "${LOADING_METHODS[@]}"; do
    echo ""
    echo "[$STRUCTURE / $LOADING]"

    for QID in $QUESTIONS; do
      COMPLETED=$((COMPLETED + 1))

      # Calculate ETA
      if [ $COMPLETED -gt 1 ]; then
        ELAPSED=$(($(date +%s) - START_TIME))
        AVG_TIME=$((ELAPSED / (COMPLETED - 1)))
        REMAINING=$((TOTAL - COMPLETED))
        ETA_SECONDS=$((AVG_TIME * REMAINING))
        ETA_MINUTES=$((ETA_SECONDS / 60))
      else
        ETA_MINUTES="?"
      fi

      OUTPUT_FILE="$RESULTS_DIR/haiku/${STRUCTURE}_${LOADING}_100_${QID}.json"

      # Skip if already exists
      if [ -f "$OUTPUT_FILE" ]; then
        printf "  [%3d/%d] %-12s %-7s %-10s ... ⏭ (exists)\n" "$COMPLETED" "$TOTAL" "$STRUCTURE" "$LOADING" "$QID"
        SKIPPED=$((SKIPPED + 1))
        continue
      fi

      printf "  [%3d/%d] %-12s %-7s %-10s (ETA: %s min)..." "$COMPLETED" "$TOTAL" "$STRUCTURE" "$LOADING" "$QID" "$ETA_MINUTES"

      # Run test
      if "$SCRIPT_DIR/run-test.sh" \
        --structure "$STRUCTURE" \
        --question "$QID" \
        --loading "$LOADING" \
        --results-dir "$RESULTS_DIR" \
        >> "$LOG_FILE" 2>&1; then
        echo " ✓"
      else
        echo " ✗"
        FAILED=$((FAILED + 1))
      fi
    done
  done
done

echo ""
echo "==================================================="
echo "  Matrix Complete"
echo "==================================================="
echo "  Total: $TOTAL"
echo "  Completed: $((COMPLETED - SKIPPED - FAILED))"
echo "  Skipped: $SKIPPED"
echo "  Failed: $FAILED"
echo "  Duration: $(( ($(date +%s) - START_TIME) / 60 )) minutes"
echo "==================================================="
